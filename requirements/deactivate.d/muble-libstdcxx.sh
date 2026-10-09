#!/usr/bin/env bash
if [[ -n "${MUBLE_OLD_LD_LIBRARY_PATH+x}" ]]; then
  export LD_LIBRARY_PATH="${MUBLE_OLD_LD_LIBRARY_PATH}"
  unset MUBLE_OLD_LD_LIBRARY_PATH
else
  unset LD_LIBRARY_PATH
fi
