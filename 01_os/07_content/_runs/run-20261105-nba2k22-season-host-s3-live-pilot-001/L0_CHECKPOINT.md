# S3 live pilot checkpoint

Status **WAITING_HUMAN_SAVE_IDENTITY**. The live process/calendar probe succeeded. L1 FULL and L2 remain pending the loaded filename. The supported Reader explicitly requires a Human-declared filename in live_world.py. The prior binding, disk hash and file modification time are evidence about files and cannot prove which one is loaded. The only input requested is the current filename. Calendar simulation is not due yet.

| Evidence | Observed |
| --- | --- |
| NBA baseline | 66f8f73f1a91597f4562b834c2acad332ad9de5b, fresh remote |
| Core contract | 877077c16bad41cfa97c1ebc9862a70ce610ff0b, fresh remote |
| Process | PID 8536, creation FILETIME 134383891808812674 |
| Build | SHA-256 1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5, PE timestamp 1652287197 |
| Schedule calendar | 2021-11-19 22:00, regular season, 1232 schedule records, 238 final and zero in-progress under native header classification |
| Mode-layer Today | 2021-11-20 00:00, mode raw 1 and period raw 29 |
| Old facts | Prior Human binding nba2k22_test_01 / MyLEAGUE0003. world-v24.sqlite is 975208448 bytes. Prior calendar observation 2021-11-19. Existing disk backups for both candidate files are readable and have distinct hashes from the current files. |

The ordinary probe used VM_READ and QUERY_LIMITED_INFORMATION, and Windows denied the handle with error 5. The first elevation wrapper invocation failed before starting a process because PowerShell returned two Python applications. The wrapper was corrected to use Python's actual interpreter. The bounded elevated read then succeeded and closed its handles. Raw failure and read receipts are in receipts/. The repeat read added PE/epoch, mode date and final-game counts.

Existing Host paths and the full capture entry were inspected. The current task branch had no active Host state or Outbox database before this probe. The pilot will use new state, ledger, Outbox and WorldData under the private sibling runtime directory s3-live-private. initialize_pilot.py checks the exact observed process and progress epoch before it creates that directory. It makes a verified copy of the declared on-disk save in the private runtime, then uses the existing Host initialization and forced new worldline against a fresh database. Neither the isolated facts database nor a plan exists yet. All changes so far are task scripts and evidence.

After the filename declaration, revalidate the live epoch, initialize the isolated WorldData binding and execute L1 FULL. Read the verified family receipts and assess GM/Coach/Player proposals before L2. Notify Human of the specific calendar step only after the first round's plan/no-change disposition. No S3 round has completed.
