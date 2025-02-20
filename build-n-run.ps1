# script argument $1 should be the python project directory
if ($args.Count -lt 1) {
    Write-Host "Usage: $PSCommandPath <path_to_python_project>"
    exit 1
}

$projectPath = $args[0]

# if the 'grader' image is not already built, build it
$graderImage = docker images -q grader 2>$null

if ([string]::IsNullOrEmpty($graderImage)) {
    docker build -t grader .
}

# run, making the container ephemeral
# TODO: don't hardcode the config file and verbosity options
docker run --rm -v "${projectPath}:/project" grader -c /app/config/2024.json -vv