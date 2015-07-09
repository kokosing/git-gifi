#!/bin/bash -e

cd $(dirname $(readlink -f $0))

VIRTUAL_ENV=virtual-env/gifi/
COMMANDS="help init install build release"
SETUP='python setup.py'

function _err() {
  echo $*
  exit 1
}

function _activate_virtual_env() {
  if [ -d $VIRTUAL_ENV ]; then
    source $VIRTUAL_ENV/bin/activate
  else
    _err "Unable to find virtual env at $VIRTUAL_ENV"
  fi
}


function init() {
  sudo apt-get install python-dev 
  virtualenv $VIRTUAL_ENV
  source $VIRTUAL_ENV/bin/activate
  _activate_virtual_env
  $SETUP develop
  pip install wheel
  pip install twine
  echo 
  echo "Remember to 'source $VIRTUAL_ENV/bin/activate', before coding"
}

function build() {
  _activate_virtual_env
  $SETUP flake8
  $SETUP test
  $SETUP install
}

function install() {
  build
  gifi install
}

function release() {
  VERSION=$(cat setup.py  | grep version | sed 's/.*0\.\(.*\)-.*/\1/g')
  _change_version 0.$VERSION
  rm -rf dist
  build
  $SETUP register
  $SETUP bdist_wheel
  $SETUP bdist_wheel --universal
  $SETUP sdist
  twine upload dist/*
  NEXT_VERSION=$(echo $VERSION + 1 | bc)
  _change_version 0.$NEXT_VERSION-SNAPSHOT
  git commit -a -m "Relase 0.$VERSION"
}

function _change_version() {
  sed 's/\(.*version=.\).*\(.,.*\)/\1'$1'\2/g' setup.py > tmp
  mv tmp setup.py
}

function help() {
  cat << EOF
$0 COMMAND [command arguments]

Commands:
  help  -   display this window
  init  -   init sandbox (install virtual env and dependencies)
  install -   install gifi to git as bunch of git aliases
EOF
}

if [[ $# = 0 ]]; then
  help
  exit
fi

COMMAND=$1
shift
echo $COMMANDS | tr ' ' '\n' | grep -q "${COMMAND}" || _err "Invalid command: $COMMAND, try help command first."

$COMMAND $*
