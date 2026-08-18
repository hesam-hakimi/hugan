cd /home/tag5916/projects/universal-coding-agent/universal-coding-agent \
&& bash scripts/safe-approve-resume.sh \
  --state-root /home/tag5916/.uca-safe-runs/phase2c-safe-v2-20260818T134704Z-369751 \
  --thread-id phase2c-safe-v2-20260818T134704Z-369751-thread \
  --repository /app1/tag5916/projects/kmai-td-genie \
  --scope-file /app1/tag5916/.uca-phase2c-safe-scope-v2/approved-scope.json \
  --host-client /app1/tag5916/projects/kmai-td-genie/.kmai-dev-agent/kmai_client.py \
  --host-python /app1/tag5916/projects/kmai-td-genie/.venv/bin/python \
  --expected-base-sha effd7ba7306021aa3561f2dcf3908a035511fd57 \
  --expected-plan-hash e63f879d68804971a0f778b27d61c2352bf762ad0da7df8de751c9ea438a2da9 \
  --expected-scope-hash 10dbb2e06da388df9f484f11b7c483f393903ad0f407d7bf78cee113a72de4715 \
  --decision approve
