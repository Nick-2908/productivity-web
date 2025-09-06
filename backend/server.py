from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for questionnaire choices
class ChronotypeChoice(str, Enum):
    EARLY_MORNING = "Early morning"
    LATE_MORNING = "Late morning" 
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    NIGHT = "Night"

class SetbackReaction(str, Enum):
    GIVE_UP = "give up"
    TRY_AGAIN_SAME = "try again same way"
    ADJUST_APPROACH = "adjust approach and try again"
    LEARN_ITERATE = "learn and iterate immediately"

class HabitCount(str, Enum):
    ZERO = "0"
    ONE_TO_TWO = "1-2"
    THREE_TO_FOUR = "3-4"
    FIVE_PLUS = "5+"

# Questionnaire Models
class QuestionnaireResponse(BaseModel):
    # Q1: What activities make you feel energized and absorbed for hours?
    energizing_activities: str
    
    # Q2: What problems are you passionate about solving?
    passionate_problems: str
    
    # Q3: What skills do you already have that you'd like to use or build? (pick up to 3)
    skills: List[str]
    
    # Q4: How many hours per weekday and weekend can you realistically devote to focused work?
    weekday_hours: float
    weekend_hours: float
    
    # Q5: When are you naturally most alert?
    chronotype: ChronotypeChoice
    
    # Q6: Do you currently do a morning routine? If yes, list key elements and duration.
    morning_routine: str
    morning_routine_duration: Optional[int] = None  # in minutes
    
    # Q7: How many existing daily habits do you reliably keep?
    habit_count: HabitCount
    
    # Q8: How do you react to setbacks?
    setback_reaction: SetbackReaction
    
    # Q9: What are 3 outcomes you want to achieve in 12 months? (three short answers, prioritized)
    outcome_1: str
    outcome_2: str
    outcome_3: str
    
    # Q10: What single habit change would make the largest difference?
    key_habit_change: str
    
    # Q11: What distractions are your biggest time sinks? (multi-select)
    distractions: List[str]
    
    # Q12: On a scale 1-10, how committed are you to following a new plan?
    commitment_level: int = Field(ge=1, le=10)

class ProfileAxes(BaseModel):
    purpose_clarity: float = Field(ge=0, le=100)
    energy_chronotype: float = Field(ge=0, le=100)
    focus_capacity: float = Field(ge=0, le=100)
    habit_foundation: float = Field(ge=0, le=100)
    mindset: float = Field(ge=0, le=100)
    skill_fit: float = Field(ge=0, le=100)

class Archetype(str, Enum):
    PURPOSE_DRIVEN_HIGH_ENERGY = "Purpose-driven + High Energy + High Focus"
    EXPLORATORY_MODERATE = "Exploratory + Moderate Energy + Moderate Habit"
    LOW_ENERGY_WANTS_CHANGE = "Low Energy / Low Habit + Wants Change"

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    questionnaire: QuestionnaireResponse
    axes: ProfileAxes
    archetype: Archetype
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HabitStack(BaseModel):
    name: str
    cue: str
    action: str
    reward: str
    tracking: str

class TimeBlock(BaseModel):
    time: str
    duration: int  # minutes
    activity: str
    type: str  # "deep_work", "routine", "break", etc.

class PlanTemplate(BaseModel):
    yearly_goal: str
    pillars: List[str]  # 3 pillars
    monthly_template: str
    weekly_template: str
    daily_template: str
    habit_stack: List[HabitStack]
    suggested_time_blocks: List[TimeBlock]
    justification: str

class UserPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    plan: PlanTemplate
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Scoring logic
def calculate_profile_axes(questionnaire: QuestionnaireResponse) -> ProfileAxes:
    """Calculate 6-axis scores from questionnaire responses"""
    
    # Q2 + Q9 -> Purpose clarity
    purpose_keywords = ["create", "build", "help", "solve", "improve", "teach", "mentor", "impact"]
    purpose_score = 0
    
    # Check Q2 for purpose keywords
    q2_lower = questionnaire.passionate_problems.lower()
    purpose_score += sum(20 for keyword in purpose_keywords if keyword in q2_lower)
    
    # Check Q9 outcomes for specificity and ambition
    outcomes = [questionnaire.outcome_1, questionnaire.outcome_2, questionnaire.outcome_3]
    specific_outcomes = sum(1 for outcome in outcomes if len(outcome.split()) > 3)
    purpose_score += specific_outcomes * 15
    
    purpose_clarity = min(100, max(0, purpose_score))
    
    # Q5 + Q6 + Q4 -> Energy & Chronotype
    chronotype_scores = {
        ChronotypeChoice.EARLY_MORNING: 90,
        ChronotypeChoice.LATE_MORNING: 70,
        ChronotypeChoice.AFTERNOON: 60,
        ChronotypeChoice.EVENING: 50,
        ChronotypeChoice.NIGHT: 30
    }
    
    energy_score = chronotype_scores[questionnaire.chronotype]
    
    # Bonus for existing morning routine
    if questionnaire.morning_routine.strip() and questionnaire.morning_routine_duration:
        energy_score += min(20, questionnaire.morning_routine_duration / 2)
    
    # Factor in available time
    avg_hours = (questionnaire.weekday_hours * 5 + questionnaire.weekend_hours * 2) / 7
    time_score = min(30, avg_hours * 5)
    energy_chronotype = min(100, energy_score + time_score)
    
    # Q1 + Q4 + Q11 -> Focus capacity
    focus_keywords = ["coding", "design", "writing", "research", "analysis", "problem", "create"]
    q1_lower = questionnaire.energizing_activities.lower()
    focus_base = sum(15 for keyword in focus_keywords if keyword in q1_lower)
    
    # Available hours factor
    hours_factor = min(40, avg_hours * 8)
    
    # Distraction penalty
    distraction_penalty = len(questionnaire.distractions) * 5
    focus_capacity = min(100, max(0, focus_base + hours_factor - distraction_penalty))
    
    # Q7 + Q10 -> Habit foundation
    habit_scores = {
        HabitCount.ZERO: 10,
        HabitCount.ONE_TO_TWO: 35,
        HabitCount.THREE_TO_FOUR: 65,
        HabitCount.FIVE_PLUS: 90
    }
    
    habit_base = habit_scores[questionnaire.habit_count]
    
    # Bonus for specific habit change identified
    if len(questionnaire.key_habit_change.strip()) > 10:
        habit_base += 15
    
    habit_foundation = min(100, habit_base)
    
    # Q8 + Q12 -> Mindset
    setback_scores = {
        SetbackReaction.GIVE_UP: 20,
        SetbackReaction.TRY_AGAIN_SAME: 40,
        SetbackReaction.ADJUST_APPROACH: 75,
        SetbackReaction.LEARN_ITERATE: 95
    }
    
    mindset_base = setback_scores[questionnaire.setback_reaction]
    commitment_bonus = questionnaire.commitment_level * 5
    mindset = min(100, mindset_base + commitment_bonus)
    
    # Q3 + Q9 -> Skill fit
    skill_count = len(questionnaire.skills)
    skill_base = min(60, skill_count * 20)
    
    # Check if outcomes align with skills
    outcomes_text = " ".join(outcomes).lower()
    skills_text = " ".join(questionnaire.skills).lower()
    
    # Simple alignment check
    skill_alignment = 0
    for skill in questionnaire.skills:
        if any(word in outcomes_text for word in skill.lower().split()):
            skill_alignment += 15
    
    skill_fit = min(100, skill_base + skill_alignment)
    
    return ProfileAxes(
        purpose_clarity=purpose_clarity,
        energy_chronotype=energy_chronotype,
        focus_capacity=focus_capacity,
        habit_foundation=habit_foundation,
        mindset=mindset,
        skill_fit=skill_fit
    )

def determine_archetype(axes: ProfileAxes) -> Archetype:
    """Determine user archetype based on axis scores"""
    
    if (axes.purpose_clarity >= 60 and 
        axes.energy_chronotype >= 70 and 
        axes.focus_capacity >= 60):
        return Archetype.PURPOSE_DRIVEN_HIGH_ENERGY
    
    elif (axes.habit_foundation < 40 and 
          axes.energy_chronotype < 60):
        return Archetype.LOW_ENERGY_WANTS_CHANGE
    
    else:
        return Archetype.EXPLORATORY_MODERATE

def generate_plan_template(profile: UserProfile) -> PlanTemplate:
    """Generate plan template based on user profile"""
    
    archetype = profile.archetype
    questionnaire = profile.questionnaire
    axes = profile.axes
    
    # Base templates by archetype
    if archetype == Archetype.PURPOSE_DRIVEN_HIGH_ENERGY:
        yearly_goal = f"Achieve {questionnaire.outcome_1} through systematic skill building and focused execution"
        pillars = [
            f"Master {questionnaire.skills[0] if questionnaire.skills else 'core skills'} through daily practice",
            f"Build sustainable systems around {questionnaire.key_habit_change}",
            "Maintain high-energy routines and deep work blocks"
        ]
        
        # Time blocks for high-energy archetype
        time_blocks = [
            TimeBlock(time="05:30", duration=30, activity="Morning routine + planning", type="routine"),
            TimeBlock(time="06:00", duration=90, activity="Deep work block 1", type="deep_work"),
            TimeBlock(time="18:00", duration=60, activity="Skill practice", type="practice")
        ]
        
    elif archetype == Archetype.LOW_ENERGY_WANTS_CHANGE:
        yearly_goal = f"Build sustainable habits and gradually work toward {questionnaire.outcome_1}"
        pillars = [
            "Establish micro-habits and daily wins",
            f"Address {questionnaire.key_habit_change} with small steps",
            "Build energy and focus capacity over time"
        ]
        
        time_blocks = [
            TimeBlock(time="07:00", duration=15, activity="Simple morning routine", type="routine"),
            TimeBlock(time="19:30", duration=30, activity="Micro-practice session", type="practice")
        ]
        
    else:  # EXPLORATORY_MODERATE
        yearly_goal = f"Explore and develop {questionnaire.outcome_1} through structured experimentation"
        pillars = [
            "Monthly skill experiments and learning sprints",
            f"Develop {questionnaire.key_habit_change} through habit stacking",  
            "Build consistent review and iteration cycles"
        ]
        
        time_blocks = [
            TimeBlock(time="06:30", duration=45, activity="Morning routine + planning", type="routine"),
            TimeBlock(time="19:00", duration=45, activity="Learning and practice", type="practice")
        ]
    
    # Generate habit stack based on archetype and responses
    habit_stack = [
        HabitStack(
            name="Morning Startup",
            cue="After waking up",
            action="Drink water + 5-minute planning",
            reward="Favorite morning beverage",
            tracking="Daily checkbox"
        ),
        HabitStack(
            name=questionnaire.key_habit_change.split()[0] + " Practice",
            cue=f"After {time_blocks[1].activity if len(time_blocks) > 1 else 'dinner'}",
            action=f"10 minutes of {questionnaire.key_habit_change}",
            reward="Track progress + celebration",
            tracking="Weekly streak counter"
        )
    ]
    
    return PlanTemplate(
        yearly_goal=yearly_goal,
        pillars=pillars,
        monthly_template="Monthly theme focus with weekly milestones and habit tracking",
        weekly_template="Weekly planning with 2-3 focus sessions and daily micro-habits",
        daily_template="Morning routine → Deep work/practice → Evening reflection",
        habit_stack=habit_stack,
        suggested_time_blocks=time_blocks,
        justification=f"{archetype.value} approach based on {axes.purpose_clarity:.0f}% purpose clarity and {axes.energy_chronotype:.0f}% energy score"
    )

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Agentic AI Productivity Coach API"}

@api_router.post("/questionnaire", response_model=UserProfile)
async def submit_questionnaire(questionnaire: QuestionnaireResponse):
    """Submit questionnaire and get user profile with archetype"""
    try:
        # Calculate profile axes
        axes = calculate_profile_axes(questionnaire)
        
        # Determine archetype
        archetype = determine_archetype(axes)
        
        # Create user profile
        profile = UserProfile(
            questionnaire=questionnaire,
            axes=axes,
            archetype=archetype
        )
        
        # Save to database
        profile_dict = profile.dict()
        profile_dict['created_at'] = profile_dict['created_at'].isoformat()
        
        await db.user_profiles.insert_one(profile_dict)
        
        return profile
        
    except Exception as e:
        logging.error(f"Error submitting questionnaire: {e}")
        raise HTTPException(status_code=500, detail="Error processing questionnaire")

@api_router.get("/profile/{profile_id}", response_model=UserProfile)
async def get_profile(profile_id: str):
    """Get user profile by ID"""
    try:
        profile_data = await db.user_profiles.find_one({"id": profile_id})
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Convert datetime string back to datetime object
        profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
        
        return UserProfile(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving profile")

@api_router.post("/plan/{profile_id}", response_model=UserPlan)
async def generate_plan(profile_id: str):
    """Generate personalized plan based on user profile"""
    try:
        # Get user profile
        profile_data = await db.user_profiles.find_one({"id": profile_id})
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
        profile = UserProfile(**profile_data)
        
        # Generate plan template
        plan_template = generate_plan_template(profile)
        
        # Create user plan
        user_plan = UserPlan(
            profile_id=profile_id,
            plan=plan_template
        )
        
        # Save to database
        plan_dict = user_plan.dict()
        plan_dict['created_at'] = plan_dict['created_at'].isoformat()
        
        await db.user_plans.insert_one(plan_dict)
        
        return user_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail="Error generating plan")

@api_router.get("/plan/{profile_id}", response_model=UserPlan)
async def get_plan(profile_id: str):
    """Get existing plan for a profile"""
    try:
        plan_data = await db.user_plans.find_one({"profile_id": profile_id})
        if not plan_data:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        plan_data['created_at'] = datetime.fromisoformat(plan_data['created_at'])
        
        return UserPlan(**plan_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting plan: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plan")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()