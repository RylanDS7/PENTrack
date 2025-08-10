#!/bin/bash

cd ../..
./PENTrack 0 test/IntegrationTest/config.in test/IntegrationTest
cd test/IntegrationTest
root -l -q ../../out/merge_all.c
rm 000000000000neutronend.out
root -l out.root showintegrationresult.cxx
