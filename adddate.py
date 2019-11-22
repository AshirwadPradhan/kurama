import yaml
import datetime

with open("servicelist.yaml", 'r') as stream:
    try:
        services = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

servicelist = ['msdb', 'msdash', 'msalert', 'msjson']
for ser, instances in services.items():
    if ser in servicelist:
        for i in instances:
            k, v = i.popitem()
            i[str(k)] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(services)
with open("servicelist.yaml", 'w') as st:
    yaml.dump(services, st)

