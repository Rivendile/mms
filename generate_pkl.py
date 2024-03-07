import pickle
from alpa_serve.profiling import ProfilingResult, ParallelConfig

path = "profiling_result_llama_opt.pkl"

data = {}

# llama2 profiling results bs=256
llama2_data = ProfilingResult("llama2-7b", {}, preprocess_cpu = 0.0, postprocess_cpu=0.0)
llama2_data.add_result(ParallelConfig(1,1,1), batch_size=1, stage_latency=[0.059769], act_mem=[0.0], weight_mem=[36851154944])
llama2_data.add_result(ParallelConfig(1,2,1), batch_size=1, stage_latency=[0.072532513], act_mem=[0.0], weight_mem=[18425577472])
llama2_data.add_result(ParallelConfig(1,1,2), batch_size=1, stage_latency=[0.03, 0.03], act_mem=[0.0], weight_mem=[18425577472, 18425577472]) # estimated
data["llama2-7b"] = llama2_data


# llama2 profiling results bs=128
opt_data = ProfilingResult("opt-13b", {}, preprocess_cpu = 0.0, postprocess_cpu=0.0)
opt_data.add_result(ParallelConfig(1,1,1), batch_size=1, stage_latency=[0.0471567], act_mem=[0.0], weight_mem=[22029380000])
opt_data.add_result(ParallelConfig(1,2,1), batch_size=1, stage_latency=[0.05746168], act_mem=[0.0], weight_mem=[11014690000])
opt_data.add_result(ParallelConfig(1,1,2), batch_size=1, stage_latency=[0.024, 0.024], act_mem=[0.0], weight_mem=[11014690000])

data["opt-13b"] = opt_data

with open(path, "wb") as handle:
    pickle.dump(data, handle)

