workloadduration=1000
workloadtype=maf1
outputvar=(0 0.05 0.1 0.15 0.2 0.25)
# ratescales=(0.000005 0.000001 0.000015 0.00002 0.000025 0.00003)
ratescales=(0.00003)

for j in ${outputvar[*]};
do
    echo output var $j
    for i in ${ratescales[*]};
    do
        echo rate scales $i
        python simulate_gpus.py --policy fcfs --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 10000
        python simulate_gpus.py --policy interleave --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 10000
        python simulate_gpus.py --policy sjmlfqmp --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 10000
        python simulate_gpus.py --policy sjmlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 10000
        python simulate_gpus.py --policy emlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 10000
    done

    for i in ${ratescales[*]};
    do
        echo rate scales $i
        python simulate_gpus.py --policy fcfs --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 5
        python simulate_gpus.py --policy interleave --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 5
        python simulate_gpus.py --policy sjmlfqmp --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 5
        python simulate_gpus.py --policy sjmlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 5
        python simulate_gpus.py --policy emlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${j} --rate-scale $i --slo-rate 5
    done
done

# qps0=(0.01 0.02 0.05 0.1 0.2 0.5)
# qps1=(0.01 0.02 0.05 0.1 0.2 0.5)
# for i in ${qps0[*]};
# do 
#     for j in ${qps1[*]};
#     do 
#         echo qps0: $i, qps1: $j
#         python simulate_1gpu.py --policy fcfs --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${outputvar} --qps0 ${i} --qps1 ${j}
#         python simulate_1gpu.py --policy interleave --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${outputvar} --qps0 ${i} --qps1 ${j}
#         python simulate_1gpu.py --policy sjmlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${outputvar} --qps0 ${i} --qps1 ${j}
#         python simulate_1gpu.py --policy emlfq --workload-duration ${workloadduration} --workload-type ${workloadtype} --output-var ${outputvar} --qps0 ${i} --qps1 ${j}
#     done
# done
