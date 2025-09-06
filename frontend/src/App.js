import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Checkbox } from "./components/ui/checkbox";
import { Slider } from "./components/ui/slider";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Separator } from "./components/ui/separator";
import { CheckCircle, Brain, Target, Zap, Habits, Growth, Focus } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QuestionnaireForm = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    energizing_activities: "",
    passionate_problems: "",
    skills: [],
    weekday_hours: 4,
    weekend_hours: 6,
    chronotype: "",
    morning_routine: "",
    morning_routine_duration: null,
    habit_count: "",
    setback_reaction: "",
    outcome_1: "",
    outcome_2: "",
    outcome_3: "",
    key_habit_change: "",
    distractions: [],
    commitment_level: 7
  });

  const skillOptions = [
    "Programming/Coding", "Design", "Writing", "Public Speaking", "Leadership",
    "Analysis", "Teaching", "Marketing", "Sales", "Research", "Project Management",
    "Creative Arts", "Communication", "Problem Solving", "Strategic Thinking"
  ];

  const distractionOptions = [
    "Social media", "Meetings", "Notifications", "Noise", "Multitasking", 
    "Email", "Phone calls", "Web browsing", "TV/Videos", "Perfectionism"
  ];

  const questions = [
    {
      title: "What activities make you feel energized and absorbed for hours?",
      subtitle: "Think about when you lose track of time in the best way",
      field: "energizing_activities",
      type: "textarea"
    },
    {
      title: "What problems are you passionate about solving?",
      subtitle: "What issues or challenges excite you to work on?",
      field: "passionate_problems", 
      type: "textarea"
    },
    {
      title: "What skills do you already have that you'd like to use or build?",
      subtitle: "Select up to 3 skills",
      field: "skills",
      type: "multi-select",
      options: skillOptions,
      maxSelections: 3
    },
    {
      title: "How many hours can you realistically devote to focused work?",
      subtitle: "Be honest about your current capacity",
      field: "hours",
      type: "hours"
    },
    {
      title: "When are you naturally most alert?",
      subtitle: "Your peak energy time of day",
      field: "chronotype",
      type: "select",
      options: ["Early morning", "Late morning", "Afternoon", "Evening", "Night"]
    },
    {
      title: "Do you currently do a morning routine?",
      subtitle: "If yes, describe key elements and duration",
      field: "morning_routine",
      type: "routine"
    },
    {
      title: "How many existing daily habits do you reliably keep?",
      subtitle: "Habits you do consistently without much effort",
      field: "habit_count",
      type: "select",
      options: ["0", "1-2", "3-4", "5+"]
    },
    {
      title: "How do you react to setbacks?",
      subtitle: "Your typical response when things don't go as planned",
      field: "setback_reaction",
      type: "select",
      options: [
        "give up",
        "try again same way", 
        "adjust approach and try again",
        "learn and iterate immediately"
      ]
    },
    {
      title: "What are 3 outcomes you want to achieve in 12 months?",
      subtitle: "List them in order of priority",
      field: "outcomes",
      type: "outcomes"
    },
    {
      title: "What single habit change would make the largest difference?",
      subtitle: "The one change that would have the biggest impact",
      field: "key_habit_change",
      type: "textarea"
    },
    {
      title: "What distractions are your biggest time sinks?",
      subtitle: "Select all that apply",
      field: "distractions",
      type: "multi-select",
      options: distractionOptions
    },
    {
      title: "How committed are you to following a new plan?",
      subtitle: "1 = not at all, 10 = absolutely committed",
      field: "commitment_level",
      type: "slider"
    }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post(`${API}/questionnaire`, formData);
      onComplete(response.data);
    } catch (error) {
      console.error("Error submitting questionnaire:", error);
    }
  };

  const renderQuestion = () => {
    const question = questions[currentStep];
    
    switch (question.type) {
      case "textarea":
        return (
          <Textarea
            value={formData[question.field]}
            onChange={(e) => handleInputChange(question.field, e.target.value)}
            placeholder="Share your thoughts..."
            className="min-h-[120px]"
          />
        );
        
      case "multi-select":
        return (
          <div className="space-y-3">
            {question.options.map(option => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox
                  id={option}
                  checked={formData[question.field].includes(option)}
                  disabled={question.maxSelections && 
                           !formData[question.field].includes(option) && 
                           formData[question.field].length >= question.maxSelections}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      handleInputChange(question.field, [...formData[question.field], option]);
                    } else {
                      handleInputChange(question.field, formData[question.field].filter(item => item !== option));
                    }
                  }}
                />
                <Label htmlFor={option} className="text-sm font-normal">
                  {option}
                </Label>
              </div>
            ))}
            {question.maxSelections && (
              <p className="text-sm text-slate-500">
                Selected: {formData[question.field].length}/{question.maxSelections}
              </p>
            )}
          </div>
        );
        
      case "select":
        return (
          <Select 
            value={formData[question.field]} 
            onValueChange={(value) => handleInputChange(question.field, value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose an option..." />
            </SelectTrigger>
            <SelectContent>
              {question.options.map(option => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
        
      case "hours":
        return (
          <div className="space-y-6">
            <div>
              <Label>Weekday hours: {formData.weekday_hours}</Label>
              <Slider
                value={[formData.weekday_hours]}
                onValueChange={(value) => handleInputChange("weekday_hours", value[0])}
                max={12}
                min={1}
                step={0.5}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Weekend hours: {formData.weekend_hours}</Label>
              <Slider
                value={[formData.weekend_hours]}
                onValueChange={(value) => handleInputChange("weekend_hours", value[0])}
                max={16}
                min={1}
                step={0.5}
                className="mt-2"
              />
            </div>
          </div>
        );
        
      case "routine":
        return (
          <div className="space-y-4">
            <Textarea
              value={formData.morning_routine}
              onChange={(e) => handleInputChange("morning_routine", e.target.value)}
              placeholder="Describe your morning routine (or write 'none' if you don't have one)..."
              className="min-h-[100px]"
            />
            {formData.morning_routine && formData.morning_routine.toLowerCase() !== 'none' && (
              <div>
                <Label>Duration (minutes)</Label>
                <Input
                  type="number"
                  value={formData.morning_routine_duration || ""}
                  onChange={(e) => handleInputChange("morning_routine_duration", parseInt(e.target.value) || null)}
                  placeholder="30"
                  className="mt-1"
                />
              </div>
            )}
          </div>
        );
        
      case "outcomes":
        return (
          <div className="space-y-4">
            <div>
              <Label>Priority 1 (Most important)</Label>
              <Input
                value={formData.outcome_1}
                onChange={(e) => handleInputChange("outcome_1", e.target.value)}
                placeholder="Your top priority outcome..."
              />
            </div>
            <div>
              <Label>Priority 2</Label>
              <Input
                value={formData.outcome_2}
                onChange={(e) => handleInputChange("outcome_2", e.target.value)}
                placeholder="Second priority..."
              />
            </div>
            <div>
              <Label>Priority 3</Label>
              <Input
                value={formData.outcome_3}
                onChange={(e) => handleInputChange("outcome_3", e.target.value)}
                placeholder="Third priority..."
              />
            </div>
          </div>
        );
        
      case "slider":
        return (
          <div className="space-y-4">
            <div className="text-center">
              <span className="text-3xl font-bold text-emerald-600">
                {formData.commitment_level}
              </span>
            </div>
            <Slider
              value={[formData.commitment_level]}
              onValueChange={(value) => handleInputChange("commitment_level", value[0])}
              max={10}
              min={1}
              step={1}
            />
            <div className="flex justify-between text-sm text-slate-500">
              <span>Not at all</span>
              <span>Absolutely committed</span>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  const progress = ((currentStep + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-slate-800">Personal Assessment</h1>
            <Badge variant="outline">
              {currentStep + 1} of {questions.length}
            </Badge>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl text-slate-800">
              {questions[currentStep].title}
            </CardTitle>
            <CardDescription className="text-slate-600">
              {questions[currentStep].subtitle}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {renderQuestion()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            Previous
          </Button>
          <Button
            onClick={handleNext}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {currentStep === questions.length - 1 ? "Complete Assessment" : "Next"}
          </Button>
        </div>
      </div>
    </div>
  );
};

const ProfileResults = ({ profile, onGeneratePlan }) => {
  const axisIcons = {
    purpose_clarity: Target,
    energy_chronotype: Zap,
    focus_capacity: Focus,
    habit_foundation: Habits,
    mindset: Growth,
    skill_fit: Brain
  };

  const axisLabels = {
    purpose_clarity: "Purpose Clarity",
    energy_chronotype: "Energy & Timing",
    focus_capacity: "Focus Capacity", 
    habit_foundation: "Habit Foundation",
    mindset: "Growth Mindset",
    skill_fit: "Skill Alignment"
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-600" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            Your Personal Profile
          </h1>
          <p className="text-slate-600">
            Based on your responses, here's your productivity archetype and strengths
          </p>
        </div>

        {/* Archetype Card */}
        <Card className="mb-8">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-emerald-700">
              {profile.archetype}
            </CardTitle>
            <CardDescription className="text-lg">
              Your personalized productivity approach
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Axes Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Object.entries(profile.axes).map(([key, value]) => {
            const Icon = axisIcons[key];
            return (
              <Card key={key}>
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <Icon className="w-6 h-6 text-emerald-600 mr-3" />
                    <h3 className="font-semibold text-slate-800">
                      {axisLabels[key]}
                    </h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-600">Score</span>
                      <span className="font-bold text-emerald-600">
                        {Math.round(value)}/100
                      </span>
                    </div>
                    <Progress value={value} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Action Button */}
        <div className="text-center">
          <Button
            onClick={onGeneratePlan}
            size="lg"
            className="bg-emerald-600 hover:bg-emerald-700 px-8 py-4 text-lg"
          >
            Generate My Personalized Plan
          </Button>
        </div>
      </div>
    </div>
  );
};

const PlanView = ({ plan, profile }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            Your Personalized Roadmap
          </h1>
          <p className="text-slate-600">
            A complete system tailored to your {profile.archetype.toLowerCase()} style
          </p>
        </div>

        {/* Yearly Goal */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl text-emerald-700">
              12-Month Vision
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg text-slate-800">{plan.plan.yearly_goal}</p>
          </CardContent>
        </Card>

        {/* Three Pillars */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {plan.plan.pillars.map((pillar, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-lg">
                  Pillar {index + 1}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-700">{pillar}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Templates Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Focus</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-700">{plan.plan.monthly_template}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Weekly Structure</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-700">{plan.plan.weekly_template}</p>
            </CardContent>
          </Card>
        </div>

        {/* Daily Template */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Daily Framework</CardTitle>
          </CardHeader>  
          <CardContent>
            <p className="text-slate-700 mb-4">{plan.plan.daily_template}</p>
            
            {/* Time Blocks */}
            <div className="space-y-3">
              <h4 className="font-semibold text-slate-800">Your Optimal Schedule:</h4>
              {plan.plan.suggested_time_blocks.map((block, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                  <div>
                    <span className="font-mono text-emerald-600">{block.time}</span>
                    <span className="ml-4 text-slate-800">{block.activity}</span>
                  </div>
                  <Badge variant="outline">{block.duration}min</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Habit Stack */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Your Habit Stack</CardTitle>
            <CardDescription>
              Micro-habits designed for sustainable growth
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {plan.plan.habit_stack.map((habit, index) => (
                <div key={index} className="border-l-4 border-emerald-500 pl-4">
                  <h4 className="font-semibold text-slate-800 mb-2">{habit.name}</h4>
                  <div className="grid sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-slate-600">Cue:</span>
                      <p className="text-slate-700">{habit.cue}</p>
                    </div>
                    <div>
                      <span className="font-medium text-slate-600">Action:</span>
                      <p className="text-slate-700">{habit.action}</p>
                    </div>
                    <div>
                      <span className="font-medium text-slate-600">Reward:</span>
                      <p className="text-slate-700">{habit.reward}</p>
                    </div>
                    <div>
                      <span className="font-medium text-slate-600">Tracking:</span>
                      <p className="text-slate-700">{habit.tracking}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Justification */}
        <Card>
          <CardHeader>
            <CardTitle>Why This Plan Works For You</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-700">{plan.plan.justification}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const Home = () => {
  const [currentView, setCurrentView] = useState("landing");
  const [userProfile, setUserProfile] = useState(null);
  const [userPlan, setUserPlan] = useState(null);

  const handleQuestionnaireComplete = (profile) => {
    setUserProfile(profile);
    setCurrentView("profile");
  };

  const handleGeneratePlan = async () => {
    try {
      const response = await axios.post(`${API}/plan/${userProfile.id}`);
      setUserPlan(response.data);
      setCurrentView("plan");
    } catch (error) {
      console.error("Error generating plan:", error);
    }
  };

  const startQuestionnaire = () => {
    setCurrentView("questionnaire");
  };

  if (currentView === "questionnaire") {
    return <QuestionnaireForm onComplete={handleQuestionnaireComplete} />;
  }

  if (currentView === "profile" && userProfile) {
    return <ProfileResults profile={userProfile} onGeneratePlan={handleGeneratePlan} />;
  }

  if (currentView === "plan" && userPlan && userProfile) {
    return <PlanView plan={userPlan} profile={userProfile} />;
  }

  // Landing Page
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-slate-800 mb-6">
              Build Your
              <span className="text-emerald-600"> Perfect Day</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
              An AI coach that creates your personalized roadmap using insights from 
              Ikigai, Atomic Habits, Deep Work, and the 5AM Club. Transform your potential 
              into systematic progress.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button
                onClick={startQuestionnaire}
                size="lg"
                className="bg-emerald-600 hover:bg-emerald-700 px-8 py-4 text-lg"
              >
                Start Your Assessment
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="px-8 py-4 text-lg"
              >
                Learn More
              </Button>
            </div>

            {/* Feature Grid */}
            <div className="grid md:grid-cols-3 gap-8 mt-16">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
                  <Brain className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Personalized Analysis</h3>
                <p className="text-slate-600">
                  Answer 12 targeted questions to reveal your unique productivity profile
                </p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
                  <Target className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Evidence-Based Plans</h3>
                <p className="text-slate-600">
                  Get roadmaps built on proven frameworks from bestselling productivity books
                </p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-full mb-4">
                  <Zap className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Actionable Systems</h3>
                <p className="text-slate-600">
                  Receive daily schedules, habit stacks, and time-blocked plans ready to implement
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;