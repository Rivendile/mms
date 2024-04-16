 python equal_model_exp.py --trace-dir /Users/test/Desktop/Rivendell/projects/llm_serving/mms/dataset/azure_v1.pkl --exp-ids metrics_vs_arrival_rates --output azure_v1_nointerleave.tsv --exp-name tech1-2_mixed_e2e --workload=azure_v1 --model-type=mixed
python equal_model_exp.py --trace-dir /Users/test/Desktop/Rivendell/projects/llm_serving/mms/dataset/azure_v1.pkl --exp-ids metrics_vs_arrival_rates --output azure_v1_interleave.tsv --exp-name tech1-2_mixed_e2e --workload=azure_v1 --model-type=mixed --enable-interleave

#  python equal_model_exp.py --trace-dir /Users/test/Desktop/Rivendell/projects/llm_serving/mms/dataset/azure_v2.pkl --exp-ids metrics_vs_arrival_rates --output azure_v2_nointerleave.tsv --exp-name tech1-2_mixed_e2e --workload=azure_v2 --model-type=mixed 

# python equal_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v1.pkl --exp-ids all --output azure_v1_1dot3b.tsv --exp-name sec6_2_data --workload=azure_v1 --model-type=bert-1.3b --parallel
# python equal_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v1.pkl --exp-ids all --output azure_v1_6dot7b.tsv --exp-name sec6_2_data --workload=azure_v1 --model-type=bert-6.7b --parallel
# python equal_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v2.pkl --exp-ids all --output azure_v2_1dot3b.tsv --exp-name sec6_2_data --workload=azure_v2 --model-type=bert-1.3b --parallel
# python equal_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v2.pkl --exp-ids all --output azure_v2_6dot7b.tsv --exp-name sec6_2_data --workload=azure_v2 --model-type=bert-6.7b --parallel

## warning, the two following commands take a long time (about 5 hours) to run
# python general_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v1.pkl --exp-ids all --output azure_v1_mixed.tsv --exp-name sec6_2_data --workload=azure_v1 --model-type=mixed --parallel
# python general_model_exp.py --trace-dir /home/ubuntu/mms/dataset/azure_v2.pkl --exp-ids all --output azure_v2_mixed.tsv --exp-name sec6_2_data --workload=azure_v2 --model-type=mixed --parallel