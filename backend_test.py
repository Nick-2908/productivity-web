import requests
import sys
import json
from datetime import datetime

class ProductivityCoachAPITester:
    def __init__(self, base_url="https://habit-roadmap.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.profile_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_submit_questionnaire(self):
        """Test questionnaire submission with realistic data"""
        questionnaire_data = {
            "energizing_activities": "coding and design work, solving complex problems, building user interfaces",
            "passionate_problems": "help students learn programming more effectively and create better educational tools",
            "skills": ["Programming/Coding", "Design", "Teaching"],
            "weekday_hours": 6.0,
            "weekend_hours": 8.0,
            "chronotype": "Early morning",
            "morning_routine": "Wake up at 5:30, drink water, 10 minutes meditation, review daily goals",
            "morning_routine_duration": 30,
            "habit_count": "3-4",
            "setback_reaction": "learn and iterate immediately",
            "outcome_1": "Launch a successful coding bootcamp for beginners",
            "outcome_2": "Build and monetize 3 educational web applications",
            "outcome_3": "Establish a consistent content creation routine",
            "key_habit_change": "consistent daily coding practice and content creation",
            "distractions": ["Social media", "Notifications", "Email"],
            "commitment_level": 9
        }

        success, response = self.run_test(
            "Submit Questionnaire",
            "POST",
            "questionnaire",
            200,
            data=questionnaire_data
        )
        
        if success and 'id' in response:
            self.profile_id = response['id']
            print(f"   Profile ID: {self.profile_id}")
            
            # Validate response structure
            required_fields = ['id', 'questionnaire', 'axes', 'archetype', 'created_at']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in response: {missing_fields}")
            else:
                print(f"   ✅ Response structure valid")
                
            # Validate axes scores
            axes = response.get('axes', {})
            expected_axes = ['purpose_clarity', 'energy_chronotype', 'focus_capacity', 
                           'habit_foundation', 'mindset', 'skill_fit']
            for axis in expected_axes:
                if axis in axes:
                    score = axes[axis]
                    if 0 <= score <= 100:
                        print(f"   ✅ {axis}: {score:.1f}/100")
                    else:
                        print(f"   ❌ {axis}: {score} (out of range 0-100)")
                else:
                    print(f"   ❌ Missing axis: {axis}")
                    
            print(f"   Archetype: {response.get('archetype', 'Not found')}")
            
        return success

    def test_get_profile(self):
        """Test getting profile by ID"""
        if not self.profile_id:
            print("❌ Skipping profile test - no profile ID available")
            return False
            
        success, response = self.run_test(
            "Get Profile by ID",
            "GET",
            f"profile/{self.profile_id}",
            200
        )
        
        if success:
            print(f"   ✅ Retrieved profile for ID: {self.profile_id}")
            
        return success

    def test_generate_plan(self):
        """Test plan generation"""
        if not self.profile_id:
            print("❌ Skipping plan generation - no profile ID available")
            return False
            
        success, response = self.run_test(
            "Generate Personalized Plan",
            "POST",
            f"plan/{self.profile_id}",
            200
        )
        
        if success:
            # Validate plan structure
            plan_data = response.get('plan', {})
            required_plan_fields = ['yearly_goal', 'pillars', 'monthly_template', 
                                  'weekly_template', 'daily_template', 'habit_stack', 
                                  'suggested_time_blocks', 'justification']
            
            missing_plan_fields = [field for field in required_plan_fields if field not in plan_data]
            if missing_plan_fields:
                print(f"   ⚠️  Missing plan fields: {missing_plan_fields}")
            else:
                print(f"   ✅ Plan structure valid")
                
            # Check specific plan elements
            pillars = plan_data.get('pillars', [])
            habit_stack = plan_data.get('habit_stack', [])
            time_blocks = plan_data.get('suggested_time_blocks', [])
            
            print(f"   Pillars count: {len(pillars)}")
            print(f"   Habit stack count: {len(habit_stack)}")
            print(f"   Time blocks count: {len(time_blocks)}")
            
            if len(pillars) == 3:
                print(f"   ✅ Correct number of pillars (3)")
            else:
                print(f"   ⚠️  Expected 3 pillars, got {len(pillars)}")
                
        return success

    def test_get_plan(self):
        """Test getting existing plan"""
        if not self.profile_id:
            print("❌ Skipping get plan test - no profile ID available")
            return False
            
        success, response = self.run_test(
            "Get Existing Plan",
            "GET",
            f"plan/{self.profile_id}",
            200
        )
        
        if success:
            print(f"   ✅ Retrieved plan for profile ID: {self.profile_id}")
            
        return success

    def test_invalid_profile_id(self):
        """Test error handling with invalid profile ID"""
        fake_id = "invalid-profile-id-12345"
        
        success, response = self.run_test(
            "Invalid Profile ID (should return 404)",
            "GET",
            f"profile/{fake_id}",
            404
        )
        
        return success

def main():
    print("🚀 Starting Productivity Coach API Tests")
    print("=" * 50)
    
    tester = ProductivityCoachAPITester()
    
    # Run all tests in sequence
    tests = [
        tester.test_root_endpoint,
        tester.test_submit_questionnaire,
        tester.test_get_profile,
        tester.test_generate_plan,
        tester.test_get_plan,
        tester.test_invalid_profile_id
    ]
    
    for test in tests:
        test()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"❌ {failed_tests} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())