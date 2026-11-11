"""The finished-wrong-answer demonstration (GATE.md, Evidence and review choices).

    python3 -m wrong_versions.demo_finished_wrong      # from the js2-loop-tools-diff folder

Runs the SAME seeded replay twice, with no network and no state write:
  1. with wrong version 1 applied (an empty board is treated as a normal observation): the run
     ends cleanly as FINISHED, exit 0, and says hubspotjobs has 0 new postings. That is wrong.
  2. with the real code: the same input ends INCOMPLETE, hubspotjobs empty-needs-review.
Then run independent_check.py on each run folder. The check reads the raw evidence, not the
loop's decision functions.
"""
from jobloop import loop
from wrong_versions import applied

SEEDED = "seeded/finished-wrong-answer"


def once(label):
    transport, config_path, state_path = loop.replay_transport(SEEDED)
    report = loop.run(transport=transport, config_path=config_path, state_path=state_path,
                      replay=SEEDED, label=label)
    loop.print_summary(report)
    return report


if __name__ == "__main__":
    print("=== 1. WRONG VERSION w01 on a SEEDED REPLAY (deliberately wrong) ===")
    with applied(1):
        wrong = once("WRONG-VERSION-w01")
    print("\n=== 2. Real code on the same SEEDED REPLAY ===")
    right = once("real-code")
    print(f"\nNow run:\n  python3 independent_check.py {wrong['run']['run_dir']}\n"
          f"  python3 independent_check.py {right['run']['run_dir']}")
