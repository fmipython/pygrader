# check if docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: docker is not installed. Please install Docker and try again. You can download and install from here: https://docs.docker.com/get-docker/"
    exit 1
}

# script argument $1 should be the python project directory
if ($args.Count -lt 1) {
    Write-Host "Usage: $PSCommandPath <path_to_python_project>"
    exit 1
}

$projectPath = $args[0]

docker pull ghcr.io/fmipython/grader:latest

# run, making the container ephemeral
# TODO: don't hardcode the config file and verbosity options
docker run --rm -v "${projectPath}:/project" fmipython/grader -c /app/config/2024.json -vv