#!/bin/bash

cd ../..
./PENTrack 0 test/HitTest/config.in test/HitTest
cd test/HitTest
root -l -q ../../out/merge_all.c
rm 000000000000neutronend.out 000000000000neutronhit.out
root -l out.root showscatterdist.cxx
