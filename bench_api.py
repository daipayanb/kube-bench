from kubernetes import client, config
import yaml
from os import path, mkdir
import time
import datetime
import shutil

# api = client.CoreV1Api()
# nodes = api.list_node()
def apply_yaml():
    #Kubectl apply the kube-bench DaemonSet .yaml file
    config.load_kube_config()
    with open(path.join(path.dirname(__file__), "job-node_DaemonSet.yaml")) as f:
        #Load the yaml file 
        daemon = yaml.safe_load(f)
        apply_resp = client.AppsV1Api().create_namespaced_daemon_set(body=daemon, namespace="default")
        print("DaemonSet created. status='%s'" % apply_resp.metadata.name)
        return apply_resp.metadata.name

def delete_apply(pods_name):
    #Delete the kube-bench DaemonSet
    delete_resp = client.AppsV1Api().delete_namespaced_daemon_set(name=pods_name, namespace="default")

def delete_old():
    #Delete results of previous scans
    if path.exists('outputs') == True:
        shutil.rmtree('outputs')
    mkdir('outputs')

def write_logs(pod_name, node_name, logs):
    #Write the ouput logs to files named Node wise 
    with open("outputs/"+ node_name,"a") as f:
        #Add time and date of scan to the beginning of the ouput file
        f.write(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+"\n")
        f.write(logs)

def get_logs(pods_name):
    #Fetch logs for the kub-bench pods
    ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
    pods = []
    for i in ret.items:
        #fetch logs of pods with pods_name = "kube-bench-node-*" 
        if( pods_name in i.metadata.name):
            print(i.metadata.name, i.spec.node_name)
            logs_response = client.CoreV1Api().read_namespaced_pod_log(name=i.metadata.name, namespace="default")
            #Write logs to the files 
            write_logs(i.metadata.name, i.spec.node_name, logs_response)

def main():
    pods_name = apply_yaml()
    time.sleep(60) 
    delete_old()
    get_logs(pods_name)
    delete_apply(pods_name)

if __name__ == "__main__":
    main()