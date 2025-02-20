# script argument $1 should be the python project directory
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_python_project>"
  exit 1
fi

# if the 'grader' image is not already built, build it
if [ "$(docker images -q grader 2> /dev/null)" == "" ]; then
  docker build -t grader .
fi

# run, making the container ephemeral
# TODO: don't hardcode the config file and verbosity options
docker run --rm -v "$1:/project" grader -c /app/config/2024.json -vv