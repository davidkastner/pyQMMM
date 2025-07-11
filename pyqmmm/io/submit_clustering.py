import os
import subprocess

# Get the current working directory
cwd = os.getcwd()

# Function to check if a directory contains any .out file
def has_out_file(dir_path):
    for file in os.listdir(dir_path):
        if file.endswith('.out'):
            return True
    return False

# Iterate over all items in the cwd
for item in os.listdir(cwd):
    item_path = os.path.join(cwd, item)
    
    # Check if it's a directory and not "1_cluster"
    if os.path.isdir(item_path) and item != "1_cluster":
        # Path to 2_analysis
        analysis_dir = os.path.join(item_path, "2_analysis")
        
        # Check if 2_analysis exists
        if os.path.exists(analysis_dir) and os.path.isdir(analysis_dir):
            # Path to 1_cluster inside 2_analysis
            cluster_dir = os.path.join(analysis_dir, "1_cluster")
            
            # Check if 1_cluster exists
            if os.path.exists(cluster_dir) and os.path.isdir(cluster_dir):
                # Iterate over subdirectories in 1_cluster
                for sub_item in os.listdir(cluster_dir):
                    sub_item_path = os.path.join(cluster_dir, sub_item)
                    
                    # Check if it's a directory
                    if os.path.isdir(sub_item_path):
                        # Path to cluster.sh
                        sh_file = os.path.join(sub_item_path, "cluster.sh")
                        
                        # Check if cluster.sh exists
                        if os.path.exists(sh_file):
                            # Check for .out files
                            if has_out_file(sub_item_path):
                                # Prompt user
                                response = input(f"Job might be running in {sub_item_path}. Resubmit? (y/N): ").strip().lower()
                                if response != 'y':
                                    print(f"Skipping resubmission for {sub_item_path}")
                                    continue
                            
                            # Submit the job
                            try:
                                result = subprocess.run(['sbatch', sh_file], capture_output=True, text=True, cwd=sub_item_path)
                                if result.returncode == 0:
                                    print(f"Submitted job for {sub_item_path}: {result.stdout.strip()}")
                                else:
                                    print(f"Error submitting job for {sub_item_path}: {result.stderr.strip()}")
                            except Exception as e:
                                print(f"Exception submitting job for {sub_item_path}: {str(e)}")
                        else:
                            print(f"cluster.sh not found in {sub_item_path}")
            else:
                print(f"1_cluster not found in {analysis_dir}")
        else:
            print(f"2_analysis not found in {item_path}")