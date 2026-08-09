def plan_interactive():
    print("┌─────────────────────────────────────────┐")
    print("│           VIREON PLAN                   │")
    print("├─────────────────────────────────────────┤")
    print("│                                         │")
    print("│ What are you validating?                │")
    print("│                                         │")
    print("│  ❯ EEG algorithm                        │")
    print("└─────────────────────────────────────────┘")
    
    print("\nWhat kind of EEG data is this?")
    print("❯ Motor imagery")
    print("  P300")
    
    print("\nWhat do you want VIREON to do?")
    print("  Quick validation")
    print("❯ Standard validation")
    
    print("\n✓ Plan saved to: plan.yaml")
    print("\nRun:")
    print("  vireon validate plan.yaml")
