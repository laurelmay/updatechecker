import json
import subprocess
import sys

def main():
    output = {}
    cmd = [
        'python3', '-m', 'pip', 'install', '-t', 'updatechecker', '-r', 'requirements.txt'
    ]
    result = subprocess.run(cmd, capture_output=True)

    output['args'] = " ".join(cmd)
    output['exit'] = str(result.returncode)
    output['stdout'] = result.stdout.decode()
    output['stderr'] = result.stderr.decode()

    print(json.dumps(output))
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())