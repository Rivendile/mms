import argparse
import os
from datetime import datetime

from alpa_serve.util import GB
from benchmarks.alpa.equal_model_case import EqualModelCase, run_equal_model_cases
from equal_model_suite import synthetic_suite, azure_v1_suite, azure_v2_suite


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="")
    parser.add_argument("--output", type=str, default="res_various_metrics.tsv")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--mode", choices=["simulate", "run"],
                        default="simulate")
    parser.add_argument("--trace-dir", type=str, default="~/azure_v2.pkl")
    parser.add_argument("--exp-ids", type=str, default="all",
                        choices=["all", "goodput_vs_num_devices", "goodput_vs_num_models",
                              "goodput_vs_slo", "goodput_vs_rate", "goodput_vs_cv",
                              "num_devices_vs_num_models", "metrics_vs_arrival_rates"])
    parser.add_argument("--model-type", type=str, default="bert-1.3b",
                        choices=["bert-1.3b", "bert-2.6b", "bert-6.7b", "bert-103.5b", "llama2-7b"])
    parser.add_argument("--mem-budget", type=int, default=40)
    parser.add_argument("--workload", type=str, default="synthetic",
                        choices=["synthetic", "azure_v1", "azure_v2"])
    parser.add_argument("--rate-distribution", choices=["uniform", "power_law"],
                        default="power_law")
    parser.add_argument("--rate", type=float, default=64)
    parser.add_argument("--cv", type=float, default=4)
    parser.add_argument('--duration', type=float, default=200)
    parser.add_argument('--enable-batching', action='store_true')
    parser.add_argument("--large-models", action="store_true")

    args = parser.parse_args()

    model_type = args.model_type
    mem_budget = args.mem_budget * GB

    # choices: {"sr-greedy", "sr-ilp", "mp-ilp", "mp-greedy-2", "mp-greedy-8"}
    if model_type == "llama2-7b" or model_type == "mixed":
        policies = ["mp-search", "llm-greedy"]

    # workload config
    if args.workload == "azure_v1":
        # real trace does not need these config
        rate_distribution = None
        total_rate = -1
        duration = -1

        fixed_num_devices, fixed_num_models, fixed_slo_scale, \
        fixed_rate_scale, fixed_cv_scale, \
        num_devices_list, num_models_list, slo_scales, \
        rate_list, cv_list, rate_scales, cv_scales = azure_v1_suite[model_type]

        arrival_process = "azure_v1"
        arrival_process_kwargs = {"rate_scale": fixed_rate_scale,
                                  "cv_scale": fixed_cv_scale,
                                  "trace_dir": args.trace_dir}
    elif args.workload == "azure_v2":
        # real trace does not need these config
        rate_distribution = None
        total_rate = -1
        duration = -1

        fixed_num_devices, fixed_num_models, fixed_slo_scale, \
        fixed_rate_scale, fixed_cv_scale, \
        num_devices_list, num_models_list, slo_scales, \
        rate_list, cv_list, rate_scales, cv_scales = azure_v2_suite[model_type]

        arrival_process = "azure_v2"
        arrival_process_kwargs = {"rate_scale": fixed_rate_scale,
                                  "cv_scale": fixed_cv_scale,
                                  "trace_dir": args.trace_dir}
    else:
        raise ValueError("Unsupported workload!")

    # output file
    if args.output.endswith(".tsv"):
        output_file_name = args.output
    else:
        output_file_name = args.output + ".tsv"

    if args.exp_name:
        os.makedirs(args.exp_name, exist_ok=True)
        output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   args.exp_name, output_file_name)
    else:
        output_folder = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   output_folder, output_file_name)

    # parse exp ids:
    if args.exp_ids == "metrics_vs_arrival_rates":
        experiments = ["metrics_vs_arrival_rates"]
    else:
        raise ValueError("Unsupported experiment!")


    cases = []
    if "metrics_vs_arrival_rates" in experiments:
        print("=== Running metrics vs. rate_scale ===")
        exp_name = "metrics_vs_arrival_rates"
        for rate_scale in [2e-3]:#rate_scales:
            for policy_name in policies:
                arrival_process_kwargs = {"rate_scale": rate_scale,
                                        "cv_scale": fixed_cv_scale,
                                        "trace_dir": args.trace_dir}
                cases.append(EqualModelCase(exp_name,
                    fixed_num_devices, mem_budget, model_type, fixed_num_models,
                    total_rate, rate_distribution,
                    arrival_process, arrival_process_kwargs,
                    fixed_slo_scale, duration, policy_name, None, None, None, None))
        
    n_cases = len(cases)
    M = 8
    n_case_each_run = (n_cases + M - 1) // M
    for i in range(M):
        start_case = i * n_case_each_run
        end_case = (i + 1) * n_case_each_run  if (i + 1) * n_case_each_run < n_cases else n_cases
        run_equal_model_cases(cases[start_case:end_case],
                              output_file=output_file,
                              mode=args.mode, parallel=args.parallel,
                              enable_batching=args.enable_batching)
    