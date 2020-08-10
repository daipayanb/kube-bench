from kubernetes import client, config
import yaml
from os import path
import time

# api = client.CoreV1Api()
# nodes = api.list_node()

def main():
    config.load_kube_config()
    with open(path.join(path.dirname(__file__), "job-node_DaemonSet.yaml")) as f:
        daemon = yaml.safe_load(f)
        apply_resp = client.AppsV1Api().create_namespaced_daemon_set(body=daemon, namespace="default")
        print("DaemonSet created. status='%s'" % apply_resp.metadata.name)
        ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
        pods = []
        time.sleep(15)    
        for i in ret.items:
            if( apply_resp.metadata.name in i.metadata.name):
                print(i.metadata.name,i.spec.node_name)
                logs_response = client.CoreV1Api().read_namespaced_pod_log(name=i.metadata.name, namespace="default")
                print(logs_response)
        delete_resp = client.AppsV1Api().delete_namespaced_daemon_set(name=apply_resp.metadata.name, namespace="default")

if __name__ == "__main__":
    main()