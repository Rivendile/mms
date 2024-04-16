# import numpy as np
import argparse
import csv
import numpy as np

EPS = 1e-6

class Request:
    def __init__(self, rid, arrival_time, workload_type, input_len, output_len, slo):
        self.rid = rid
        self.arrival_time = arrival_time
        self.workload_type = workload_type
        self.input_len = input_len
        self.output_len = output_len
        self.finish_time = None
        self.latency = None
        self.slo = slo
        self.cur_token = -1 # -1 for not served; 0 for finish input; 1-n for output token
        self.priority = None
        self.prio_quan = None
        self.last_exec_time = arrival_time

    def get_next_process_time(self):
        if self.cur_token==-1:
            return self.input_len*workloads_dict[self.workload_type].info_args["t_in"]
        else:
            return workloads_dict[self.workload_type].info_args["t_out"]

    def process_token(self):
        self.cur_token += 1
        if self.cur_token == self.output_len:
            return True
        else:
            return False

class Workload:
    def __init__(self, workload_type, info_args):
        self.workload_type = workload_type
        self.info_args = info_args

def generate_workloads():
    info1 = {"qps": args.qps1, "t_in": TIME_UNIT, "st_len_in": 30, "t_out": TIME_UNIT, "st_len_out": 5}
    info0 = {"qps": args.qps0, "t_in": TIME_UNIT, "st_len_in": 1, "t_out": TIME_UNIT*2, "st_len_out": 100}
    workload0 = Workload("job0", info0)
    workload1 = Workload("job1", info1)
    workloads_dict = {"job0":workload0, "job1":workload1}
    return workloads_dict

def generate_requests():
    if args.workload_type in ["mixed", "single"]:
        qps0 = workloads_dict["job0"].info_args["qps"]
        qps1 = workloads_dict["job1"].info_args["qps"]
        arrival_time0 = []
        for x in range(int(qps0*args.workload_duration)):
            arrival_time0.append((x/qps0, "job0"))
        if args.workload_type == "mixed":
            for x in range(int(qps1*args.workload_duration)):
                arrival_time0.append((x/qps1, "job0"))
        arrival_time1 = []
        for x in range(int(qps1*args.workload_duration)):
            arrival_time1.append((x/qps1, "job1"))
        if args.workload_type == "mixed":
            for x in range(int(qps0*args.workload_duration)):
                arrival_time1.append((x/qps0, "job1"))
        arrival_time = arrival_time1 + arrival_time0
        arrival_time.sort(key=lambda x:x[0])

        # output follows normal distribution
        mean0 = workloads_dict["job0"].info_args["st_len_out"]
        var0 = mean0*args.output_var
        mean1 = workloads_dict["job1"].info_args["st_len_out"]
        var1 = mean1*args.output_var
        requests = []
        cur_rid = 0
        for x in arrival_time:
            stamp, w_type = x
            w_info = workloads_dict[w_type].info_args
            if w_type == "job0":
                output_len = max(1, int(np.random.normal(mean0, var0)))
            else:
                output_len = max(1, int(np.random.normal(mean1, var1)))
            r_time = w_info["t_in"]*w_info["st_len_in"]+w_info["t_out"]*output_len
            slo = r_time*SLO_RATE
            request = Request(cur_rid, stamp, w_type, w_info["st_len_in"], output_len, slo)
            cur_rid += 1
            requests.append(request)

        return requests
    elif args.workload_type == "maf1":
        from alpa_serve.trace import Trace

        train_start = "0.0.0"
        train_end = "0.1.0"
        azure_v1_trace_dir = "dataset/azure_v1.pkl"
        azure_v1_trace = Trace("azure_v1", azure_v1_trace_dir)
        rate_scale = args.rate_scale
        num_models = 2
        model_names = [f"job{i}" for i in range(num_models)]
        train_replays = azure_v1_trace.replay(model_names, model_mapping_strategy="round_robin", arrival_distribution="gamma", start_time=train_start, end_time=train_end, interval_seconds=60, rate_scale_factor=rate_scale, cv_scale_factor=1)

        mean0 = workloads_dict["job0"].info_args["st_len_out"]
        var0 = mean0*args.output_var
        mean1 = workloads_dict["job1"].info_args["st_len_out"]
        var1 = mean1*args.output_var
        # for x in train_replays.arrivals:
        arrival_time = []
        for model_name in model_names:
            for arrival in train_replays[model_name].arrivals:
                arrival_time.append((arrival, model_name))
        arrival_time.sort(key=lambda x:x[0])

        requests = []
        cur_rid = 0
        for x in arrival_time:
            stamp, w_type = x
            w_info = workloads_dict[w_type].info_args
            if w_type == "job0":
                output_len = max(1, int(np.random.normal(mean0, var0)))
            else:
                output_len = max(1, int(np.random.normal(mean1, var1)))
            r_time = w_info["t_in"]*w_info["st_len_in"]+w_info["t_out"]*output_len
            slo = r_time*SLO_RATE
            request = Request(cur_rid, stamp, w_type, w_info["st_len_in"], output_len, slo)
            cur_rid += 1
            requests.append(request)

        return requests

def get_metrics(requests):
    latencys = {}
    tokens = {}
    duration = {}
    counts = {}
    norm_latencys = {}
    for key in workloads_dict.keys():
        duration[key] = args.workload_duration if args.workload_type == "single" else args.workload_duration*2
    for r in requests:
        if r.finish_time != None :
            if r.workload_type not in latencys:
                latencys[r.workload_type] = []
                tokens[r.workload_type] = []
                duration[r.workload_type] = 0
                norm_latencys[r.workload_type] = []
            latencys[r.workload_type].append(r.latency)
            w_info = workloads_dict[r.workload_type].info_args
            rtime = w_info["t_in"]*w_info["st_len_in"]+w_info["t_out"]*w_info["st_len_out"]
            norm_latencys[r.workload_type].append(r.latency/rtime)
            tokens[r.workload_type].append(r.output_len)
            duration[r.workload_type] = max(duration[r.workload_type], r.finish_time)
        if r.workload_type not in counts:
            counts[r.workload_type] = 0
        counts[r.workload_type] += 1
    
    metrics = {}
    all_latency = []
    all_norm_latency = []
    all_duration = args.workload_duration if args.workload_type == "single" else args.workload_duration*2
    all_tokens = []
    all_counts = len(requests)
    for key, val in latencys.items():
        val.sort()
        metrics[key]={}
        metrics[key]["avg_latency"] = sum(val)/len(val)
        metrics[key]['norm_latency'] = sum(norm_latencys[key])/len(norm_latencys[key])
        metrics[key]["p99_latency"] = val[int(len(val)*0.99)]
        metrics[key]["r_tput"] = len(val)/duration[key] if duration[key]>0 else 0
        metrics[key]["t_tput"] = sum(tokens[key])/duration[key] if duration[key]>0 else 0
        metrics[key]["slo_attainment"] = len(val)/counts[key]

        all_latency.extend(val)
        all_norm_latency.extend(norm_latencys[key])
        all_duration = max(all_duration, duration[key])
        all_tokens.extend(tokens[key])
        # all_counts += counts[key]
    
    metrics["overall"] = {}
    metrics["overall"]["avg_latency"] = sum(all_latency)/len(all_latency) if len(all_latency)>0 else 0
    metrics["overall"]["norm_latency"] = sum(all_norm_latency)/len(all_norm_latency) if len(all_norm_latency)>0 else 0
    metrics["overall"]["p99_latency"] = all_latency[int(len(val)*0.99)] if len(all_latency)>0 else 0
    metrics["overall"]["r_tput"] = len(all_latency)/all_duration
    metrics["overall"]["t_tput"] = sum(all_tokens)/all_duration
    metrics["overall"]["slo_attainment"] = len(all_latency)/all_counts if all_counts>0 else 0
    
    return metrics

def simulate_fcfs(requests, w_dict):
    tmp_device_time = 0
    max_kv = 0
    for r in requests:
        tmp_device_time = max(r.arrival_time, tmp_device_time)
        while True:
            next_time = r.get_next_process_time()
            if tmp_device_time+next_time-r.arrival_time<=r.slo+EPS:
                tmp_device_time += next_time
                finish_flag = r.process_token()
                max_kv = max(max_kv, r.cur_token)
                if finish_flag:
                    r.finish_time = tmp_device_time
                    r.latency = r.finish_time - r.arrival_time
                    break
            else:
                break

    return get_metrics(requests), max_kv

def calc_kv(requests_queue):
    sum_kv = 0
    for r in requests_queue:
        sum_kv += max(0, r.cur_token)
    return sum_kv

def simulate_interleave(requests, w_dict):
    tmp_device_time = 0
    next_event_time = requests[0].arrival_time
    requests_queue = []
    cur_rid = 0
    max_kv = 0
    while True:
        if cur_rid>=len(requests) and len(requests_queue)==0:
            # finish all requests
            break

        # process past event
        if len(requests_queue)>0:
            if tmp_device_time+requests_queue[0].get_next_process_time()<=next_event_time:
                finish_flag = requests_queue[0].process_token()
                tmp_time = tmp_device_time+requests_queue[0].get_next_process_time()
                if finish_flag:
                    if tmp_time-requests_queue[0].arrival_time<=requests_queue[0].slo:
                        requests_queue[0].finish_time = tmp_time
                        requests_queue[0].latency = tmp_time - requests_queue[0].arrival_time
                    requests_queue.pop(0)
                else:
                    r = requests_queue[0]
                    requests_queue.pop(0)
                    if tmp_time-r.arrival_time<=r.slo:
                        requests_queue.append(r)
            max_kv = max(max_kv, calc_kv(requests_queue))
        
        tmp_device_time = next_event_time
        # add new event
        while cur_rid<len(requests) and requests[cur_rid].arrival_time<=tmp_device_time:
            requests_queue.append(requests[cur_rid])
            cur_rid+=1
        
        # get next event
        next_event_time = float("inf")
        if cur_rid<len(requests):
            next_event_time = min(next_event_time, requests[cur_rid].arrival_time)
        if len(requests_queue)>0:
            next_event_time = min(next_event_time, tmp_device_time+requests_queue[0].get_next_process_time())
    
    return get_metrics(requests), max_kv
        
def get_priority(last_prio, cur_itertime):
    cur_itertime = int(cur_itertime / TIME_UNIT)
    new_prio = 1 if last_prio==0 else last_prio*2
    while cur_itertime>new_prio:
        new_prio *= 2
    return new_prio

def simulate_sjmlfq(requests, w_dict):
    tmp_device_time = requests[0].arrival_time
    requests_queue = {}
    cur_rid = 0
    max_kv = 0
    starvation_limit = args.workload_duration*SLO_RATE
    while True:
        left_requests = 0
        for prio, val in requests_queue.items():
            left_requests += len(val)
        if cur_rid>=len(requests) and left_requests == 0:
            # finish all requests
            break
        
        # print(cur_rid, len(requests), len(requests_queue), tmp_device_time)

        # add new requests
        while cur_rid<len(requests) and requests[cur_rid].arrival_time<=tmp_device_time:
            cur_prio = get_priority(0, requests[cur_rid].input_len*workloads_dict[requests[cur_rid].workload_type].info_args["t_in"])
            requests[cur_rid].priority = cur_prio
            requests[cur_rid].prio_quan = cur_prio
            if cur_prio not in requests_queue:
                requests_queue[cur_prio] = []
            requests_queue[cur_prio].append(requests[cur_rid])
            cur_rid += 1
        
        # process requests
        for prio, rs in requests_queue.items():
            pr_rs = []
            for r in rs:
                if tmp_device_time - r.arrival_time <= r.slo:
                    pr_rs.append(r)
            requests_queue[prio] = rs

        # demote requests
        add_prio = []
        for prio, rs in requests_queue.items():
            for r in rs:
                next_iter_time = r.get_next_process_time()
                if r.prio_quan<next_iter_time/TIME_UNIT:
                    old_prio = r.priority
                    new_prio = get_priority(old_prio, next_iter_time)
                    if new_prio not in requests_queue:
                        add_prio.append(new_prio)
        for prio in add_prio:
            requests_queue[prio] = []
        for prio, rs in requests_queue.items():
            pr_rs = []
            for r in rs:
                next_iter_time = r.get_next_process_time()
                if r.prio_quan<next_iter_time/TIME_UNIT:
                    old_prio = r.priority
                    r.priority = get_priority(old_prio, next_iter_time)
                    r.prio_quan = r.priority
                    assert r.priority in requests_queue
                    requests_queue[r.priority].append(r)
                else:
                    pr_rs.append(r)
            requests_queue[prio] = pr_rs
        # promote requests
        for prio, rs in requests_queue.items():
            pr_rs = []
            if prio==1:
                continue
            for r in rs:
                if tmp_device_time - r.last_exec_time >= starvation_limit:
                    r.priority = 1
                    r.prio_quan = r.get_next_process_time()
                    requests_queue[r.priority].append(r)
                else:
                    pr_rs.append(r)
            requests_queue[prio] = pr_rs
        
        # calc kv
        tmp_kv = 0
        for prio, rs in requests_queue.items():
            for r in rs:
                tmp_kv = max(tmp_kv, r.cur_token)
        max_kv = max(max_kv, tmp_kv)
        
        # execute requests
        process_flag = False
        for prio, rs in requests_queue.items():
            if len(rs)==0:
                continue
            r = rs[0]
            next_iter_time = r.get_next_process_time()
            tmp_device_time += next_iter_time
            r.last_exec_time = tmp_device_time
            finish_flag = r.process_token()
            r.prio_quan -= next_iter_time / TIME_UNIT
            assert r.prio_quan >= 0
            if tmp_device_time - r.arrival_time > r.slo:
                rs.pop(0)
            elif finish_flag:
                r.finish_time = tmp_device_time
                r.latency = r.finish_time - r.arrival_time
                rs.pop(0)
            process_flag = True
            break
        if not process_flag:
            if cur_rid < len(requests):
                tmp_device_time = requests[cur_rid].arrival_time


    return get_metrics(requests), max_kv

    

def simulate_emlfq(requests, w_dict):
    tmp_device_time = requests[0].arrival_time
    requests_queue = []
    cur_rid = 0
    max_kv = 0
    starvation_limit = args.workload_duration*SLO_RATE
    # To do
    while True:
        if cur_rid>=len(requests) and len(requests_queue) == 0:
            # finish all requests
            break
        
        # print(tmp_device_time, cur_rid, len(requests), len(requests_queue))
        # add new requests
        while cur_rid<len(requests) and requests[cur_rid].arrival_time<=tmp_device_time+EPS:
            w_type = requests[cur_rid].workload_type
            requests[cur_rid].priority = requests[cur_rid].input_len*workloads_dict[w_type].info_args["t_in"]+workloads_dict[w_type].info_args["st_len_out"]*workloads_dict[w_type].info_args["t_out"] *(1+2*args.output_var)
            requests_queue.append(requests[cur_rid])
            requests[cur_rid].prio_quan = requests[cur_rid].priority
            cur_rid += 1
        
        # print(tmp_device_time, cur_rid, len(requests), len(requests_queue))

        pr_requests_queue = []
        for r in requests_queue:
            if tmp_device_time - r.arrival_time <= r.slo+EPS:
                pr_requests_queue.append(r)
        requests_queue = pr_requests_queue

        # calc kv
        tmp_kv = 0
        for r in requests_queue:
            tmp_kv = max(tmp_kv, r.cur_token)
        max_kv = max(max_kv, tmp_kv)

        # execute requests
        process_flag = False
        while len(requests_queue)>0 and not process_flag:
            requests_queue.sort(key=lambda x: x.priority)
            r = requests_queue[0]
            next_iter_time = r.get_next_process_time()
            if r.priority - next_iter_time >= -EPS:
                process_flag = True
                tmp_device_time += next_iter_time
                r.priority -= next_iter_time
                finish_flag = r.process_token()
                # print("process: ", r.rid, r.priority, next_iter_time, finish_flag)
                if finish_flag:
                    r.finish_time = tmp_device_time
                    r.latency = r.finish_time - r.arrival_time
                    requests_queue.pop(0)
            else:
                r.priority = r.prio_quan * 2
                r.prio_quan = r.priority
        
        if not process_flag:
            if cur_rid < len(requests):
                tmp_device_time = requests[cur_rid].arrival_time
        
    return get_metrics(requests), max_kv


    
def print_metrics(metrics, max_kv):
    print("----------\n", args.policy)
    for key in list(workloads_dict.keys())+["overall"]:
        if key in metrics:
            val = metrics[key]
            if key!="overall":
                print(key, workloads_dict[key].info_args)
            print(f"{key}: avg latency: {val['avg_latency']}, p99 latency: {val['p99_latency']}, request tput: {val['r_tput']}, token tput: {val['t_tput']}, slo attainment: {val['slo_attainment']}")
        else:
            print(key, workloads_dict[key].info_args)
            print(f"{key}: avg latency: 0, p99 latency: 0, request tput: 0, token tput: 0, slo attainment: 0")

    print(f"Max kv used: {max_kv}")

    with open(args.output_filename+".csv", "a") as csvfile:
        writer = csv.writer(csvfile)

        # writer.writerow(["avg latency0", "p99 latency0", "r_tput0", "t_tput0", "slo_attainment0", "avg latency1", "p99 latency1", "r_tput1", "t_tput1", "slo_attainment1","avg latency all", "p99 latency all", "r_tput all", "t_tput all", "slo_attainment all"])
        write_content = [args.policy, args.output_var, args.rate_scale]
        # for val_str in ["job0", "job1", "overall"]:
        #     if val_str in metrics:p
        #         val = metrics[val_str]
        #         write_content += [val['avg_latency'], val['p99_latency'], val['r_tput'], val['t_tput'], val['slo_attainment']]
        #     else:
        #         write_content += [0,0,0,0,0]
        for metric_str in ["avg_latency", "norm_latency", "p99_latency", "r_tput", "t_tput", "slo_attainment"]:
            for val_str in ["job0", "job1", "overall"]:
                if val_str in metrics:
                    val = metrics[val_str][metric_str]
                else:
                    val = 0
                write_content.append(val)
        writer.writerow(write_content)

def print_requests(requests):
    for r in requests:
        exec_time = r.input_len*workloads_dict[r.workload_type].info_args["t_in"] + r.output_len*workloads_dict[r.workload_type].info_args["t_out"]
        print(r.arrival_time, r.workload_type, r.finish_time, r.latency, exec_time, r.slo)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=["fcfs", "interleave", "sjmlfq", "emlfq"])
    parser.add_argument("--workload-duration", type=int, default=1000)
    parser.add_argument("--workload-type", choices=["mixed", "single", "maf1", "maf2"])
    parser.add_argument("--qps0", type=float, default=0.02)
    parser.add_argument("--qps1", type=float, default=0.1)
    parser.add_argument("--rate-scale", type=float, default=0.1)
    parser.add_argument("--output-var", type=float, default=0) # use normal distribution 0-1
    parser.add_argument("--output-filename", type=str, default="test")
    parser.add_argument("--slo-rate", type=float, default="5")
    parser.add_argument("--time-unit", type=float, default=0.05)
    # parser.add_argument("")

    args = parser.parse_args()
    TIME_UNIT = args.time_unit
    if args.slo_rate>1000:
        SLO_RATE = float("inf")
    else:
        SLO_RATE = args.slo_rate

    workloads_dict = generate_workloads()
    requests = generate_requests()

    # print_requests(requests)
    # exit()

    if args.policy == "fcfs":
        metrics, max_kv = simulate_fcfs(requests, workloads_dict)
    elif args.policy == "interleave":
        metrics, max_kv = simulate_interleave(requests, workloads_dict)
    elif args.policy == "sjmlfq":
        metrics, max_kv = simulate_sjmlfq(requests, workloads_dict)
    elif args.policy == "emlfq":
        metrics, max_kv = simulate_emlfq(requests, workloads_dict)
    
    print_metrics(metrics, max_kv)

    print_requests(requests)