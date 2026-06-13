from QuartetFuzz_Gateway import CampaignController, CrashDeduplicator

def test_deduplicator():
    print("Running Deduplicator Test...")
    deduper = CrashDeduplicator()
    err1 = "Traceback (most recent call last):\nFile 'test.py', line 10\nZeroDivisionError: division by zero\n"
    err2 = "Some other path info...\nTraceback (most recent call last):\nFile 'test.py', line 10\nZeroDivisionError: division by zero\n"
    
    assert deduper.add_and_check(err1) == True
    assert deduper.add_and_check(err1) == False
    assert deduper.add_and_check(err2) == False
    print("Deduplicator Test Passed!")

def test_baseline_block():
    print("Running Baseline Block Test...")
    controller = CampaignController("009")
    bad_harness = """
def run_target():
    print(1/0) # Fails immediately
"""
    res = controller.run_fuzzing_campaign(bad_harness, "val", 10, max_iters=5)
    assert res['status'] == "HARNESS_BROKEN"
    print("Baseline Block Test Passed!")

def test_mutation_kill():
    print("Running Mutation Kill Test...")
    controller = CampaignController("009")
    
    # We create a target that crashes only if string length is 5
    target_harness = """
def run_target():
    # If val is exactly 5 characters long, this will divide by zero
    # Or if val is not a string, let's ignore
    if isinstance(val, str) and len(val) == 5:
        a = 1 / 0
    else:
        pass
"""
    # Provide a string seed "test"
    res = controller.run_fuzzing_campaign(target_harness, "val", "test", max_iters=100)
    
    # We hope our mutator eventually produces a string of length 5 or triggers another error.
    # Actually our mutator doesn't specifically target length 5, but it might do val + "\x00" which is len 5.
    # Let's see if it found any crashes.
    print(f"Crashes found: {res.get('crashes', 0)}")
    assert res['status'] == "COMPLETED"
    assert res.get('crashes', 0) > 0, "Expected mutator to find at least 1 crash!"
    print("Mutation Kill Test Executed!")

if __name__ == "__main__":
    test_deduplicator()
    test_baseline_block()
    test_mutation_kill()
    print("All Fuzzing Gateway tests passed!")
