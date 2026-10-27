#!/bin/bash
# Parameter-influence evaluation (RQ3): interaction size t, trimming iterations m,
# and cache size c, instance-set variant only.
#
# For each model, runs the sampler with r repetitions (default 10):
#   - t experiment: t in {1,2,3},    m = 5, c = 50   -> sampling time
#   - c experiment: c in {50,500,1000}, t = 2, m = 5   -> sampling time
#   - m experiment: m in {1,5,10,15,20}, t = 2, c = 50 -> sampling time + sample size
# The experiments run cheapest-first (t, then c, then m) and the parameter
# values within each experiment are also ordered by increasing cost.
#
# Usage:
#   ./run_parameter_eval.sh [--r 10] [--model-r STEM:R] [--out DIR]
#                           [--experiments t,c,m] [--models-dir DIR]
#                           [MODEL.json ...]
#
# --model-r overrides the repetition count for one model, e.g. --model-r model_b:5
# (repeatable). If no model files are given, all *.json in --models-dir are used;
# pass model files in the desired execution order (e.g. cheapest models first).
# Logs land in $OUT as {time,size}_{exp}_{value}_{model-stem}.log plus
# walltimes.csv with rows "kind,exp,value,stem,r,wall=N". Parse afterwards with:
#   python3 parse_parameter_eval_results.py --results-dir "$OUT"

set -u

R=10
OUT=tests/eval/param_results
EXPERIMENTS=t,c,m
MODELS_DIR=tests/eval/models
MODEL_R=""
MODELS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --r) R="$2"; shift 2 ;;
    --model-r) MODEL_R="$MODEL_R $2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --experiments) EXPERIMENTS="$2"; shift 2 ;;
    --models-dir) MODELS_DIR="$2"; shift 2 ;;
    *) MODELS+=("$1"); shift ;;
  esac
done

r_for() {
  local stem r pair
  stem=$(basename "$1" .json)
  r=$R
  for pair in $MODEL_R; do
    [ "${pair%%:*}" = "$stem" ] && r="${pair##*:}"
  done
  echo "$r"
}

if [ ${#MODELS[@]} -eq 0 ]; then
  for f in "$MODELS_DIR"/*.json; do
    [ -e "$f" ] && MODELS+=("$f")
  done
fi
if [ ${#MODELS[@]} -eq 0 ]; then
  echo "No models found. Pass model files or put them in $MODELS_DIR." >&2
  exit 1
fi

mkdir -p "$OUT"
IFS=',' read -r -a EXPERIMENTS_ARR <<< "$EXPERIMENTS"

for model in "${MODELS[@]}"; do
  stem=$(basename "$model" .json)
  r_model=$(r_for "$model")
  echo "=== $model (r=$r_model) ==="
  for exp in "${EXPERIMENTS_ARR[@]}"; do
    case "$exp" in
      t) PARAMS=(1 2 3); KINDS=(time) ;;
      m) PARAMS=(1 5 10 15 20); KINDS=(time size) ;;
      c) PARAMS=(50 500 1000); KINDS=(time) ;;
      *) echo "Unknown experiment '$exp' (expected t, m or c)" >&2; exit 1 ;;
    esac
    for param in "${PARAMS[@]}"; do
      for kind in "${KINDS[@]}"; do
        case "$exp" in
          t) t=$param; m=5; c=50 ;;
          m) t=2; m=$param; c=50 ;;
          c) t=2; m=5; c=$param ;;
        esac
        if [ "$kind" = time ]; then
          cmd=(evaluate-t-wise --t "$t" --m "$m" --cache-size "$c" --r "$r_model")
        else
          cmd=(evaluate-t-wise-sample-size --t "$t" --m "$m" --cache-size "$c" --r "$r_model")
        fi
        log="$OUT/${kind}_${exp}_${param}_${stem}.log"
        start=$(date +%s)
        poetry run cfmtoolbox --import "$model" "${cmd[@]}" > "$log" 2>&1
        end=$(date +%s)
        echo "$kind,$exp,$param,$stem,$r_model,wall=$((end - start))" >> "$OUT/walltimes.csv"
        echo "  done $log ($((end - start))s)"
      done
    done
  done
done
echo PARAM_EVAL_DONE >> "$OUT/walltimes.csv"
