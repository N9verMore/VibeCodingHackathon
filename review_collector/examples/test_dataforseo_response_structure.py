#!/usr/bin/env python3
"""
Test to verify DataForSEO API response structure parsing

This script tests that we correctly parse the tasks_ready endpoint response
according to the official DataForSEO documentation:
https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready/

The key issue was that ready tasks are in tasks[].result[], not tasks[].
"""

# Mock response from DataForSEO tasks_ready endpoint
# Source: https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready/
MOCK_TASKS_READY_RESPONSE = {
    "version": "0.1.20210917",
    "status_code": 20000,
    "status_message": "Ok.",
    "time": "0.1630 sec.",
    "cost": 0,
    "tasks_count": 1,
    "tasks_error": 0,
    "tasks": [
        {
            "id": "11011442-2806-0357-0000-87f90d2ac78d",
            "status_code": 20000,
            "status_message": "Ok.",
            "time": "0.0910 sec.",
            "cost": 0,
            "result_count": 4,
            "path": [
                "v3",
                "business_data",
                "trustpilot",
                "reviews",
                "tasks_ready"
            ],
            "data": {
                "api": "business_data",
                "function": "reviews",
                "se": "trustpilot",
                "se_type": "reviews"
            },
            "result": [
                {
                    "id": "11011325-2806-0358-0000-319578bfdc9e",
                    "se": "trustpilot",
                    "se_type": "reviews",
                    "date_posted": "2021-11-01 11:25:06 +00:00",
                    "tag": "",
                    "endpoint": "/v3/business_data/trustpilot/reviews/task_get/11011325-2806-0358-0000-319578bfdc9e"
                },
                {
                    "id": "11011344-2806-0358-0000-7e4c7679e45d",
                    "se": "trustpilot",
                    "se_type": "reviews",
                    "date_posted": "2021-11-01 11:44:30 +00:00",
                    "tag": "",
                    "endpoint": "/v3/business_data/trustpilot/reviews/task_get/11011344-2806-0358-0000-7e4c7679e45d"
                },
                {
                    "id": "11011401-2806-0358-0000-b66cd0c14b32",
                    "se": "trustpilot",
                    "se_type": "reviews",
                    "date_posted": "2021-11-01 12:01:19 +00:00",
                    "tag": "",
                    "endpoint": "/v3/business_data/trustpilot/reviews/task_get/11011401-2806-0358-0000-b66cd0c14b32"
                },
                {
                    "id": "11011421-2806-0358-0000-7017ae7d8ee5",
                    "se": "trustpilot",
                    "se_type": "reviews",
                    "date_posted": "2021-11-01 12:21:45 +00:00",
                    "tag": "",
                    "endpoint": "/v3/business_data/trustpilot/reviews/task_get/11011421-2806-0358-0000-7017ae7d8ee5"
                }
            ]
        }
    ]
}


def test_old_incorrect_parsing(data, target_task_id):
    """
    OLD (INCORRECT) way - searching in tasks[] directly
    This WILL NOT WORK according to DataForSEO docs
    """
    print("\n❌ Testing OLD (incorrect) parsing:")
    print(f"   Looking for task_id: {target_task_id}")
    
    tasks = data.get('tasks', [])
    for task in tasks:
        if task.get('id') == target_task_id:
            print(f"   ✓ Found task: {task.get('id')}")
            return True
    
    print(f"   ✗ Task NOT found (this is expected with old code)")
    return False


def test_new_correct_parsing(data, target_task_id):
    """
    NEW (CORRECT) way - searching in tasks[].result[]
    According to DataForSEO docs: https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready/
    """
    print("\n✅ Testing NEW (correct) parsing:")
    print(f"   Looking for task_id: {target_task_id}")
    
    tasks = data.get('tasks', [])
    for task in tasks:
        result = task.get('result', [])
        print(f"   Checking task container: {task.get('id')} (has {len(result)} ready tasks)")
        for ready_task in result:
            if ready_task.get('id') == target_task_id:
                print(f"   ✓ Found task in result[]: {ready_task.get('id')}")
                print(f"   ✓ Endpoint: {ready_task.get('endpoint')}")
                return True
    
    print(f"   ✗ Task NOT found")
    return False


def main():
    print("=" * 70)
    print("DataForSEO API Response Structure Test")
    print("=" * 70)
    print("\nAccording to official docs:")
    print("https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready/")
    print("\nReady tasks are in: tasks[].result[] (NOT in tasks[])")
    
    # Test with one of the task IDs from mock response
    target_task_id = "11011344-2806-0358-0000-7e4c7679e45d"
    
    # Test old way (should fail)
    old_found = test_old_incorrect_parsing(MOCK_TASKS_READY_RESPONSE, target_task_id)
    
    # Test new way (should succeed)
    new_found = test_new_correct_parsing(MOCK_TASKS_READY_RESPONSE, target_task_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print(f"Old parsing (tasks[]): {'✓ FOUND' if old_found else '✗ NOT FOUND'}")
    print(f"New parsing (tasks[].result[]): {'✓ FOUND' if new_found else '✗ NOT FOUND'}")
    
    if new_found and not old_found:
        print("\n✅ SUCCESS! New parsing works correctly!")
    elif old_found:
        print("\n⚠️ WARNING! Old parsing found task (this shouldn't happen)")
    else:
        print("\n❌ ERROR! Neither parsing method found the task")
    
    print("\n" + "=" * 70)
    print("Structure visualization:")
    print("=" * 70)
    print("""
Correct structure according to DataForSEO docs:
{
  "tasks": [                           ← Top-level container
    {
      "id": "container-id",            ← Container ID (not the task we want)
      "result": [                      ← Array of READY tasks
        {
          "id": "actual-task-id",      ← This is the task ID we're looking for!
          "endpoint": "..."
        }
      ]
    }
  ]
}
    """)


if __name__ == '__main__':
    main()

