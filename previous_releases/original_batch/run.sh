#!/bin/sh
#run.sh

#Runs a FDPB calculation (and titration) on the cluster

UHBD_EXEC=$UHBD/bin.gnu
UHBD_VERS=uhbd

echo 'Running prepares'
$UHBD_EXEC/prepares

echo 'Running UHBD'
$UHBD_EXEC/$UHBD_VERS < pkaS-uhbdini.inp > pkaS-uhbdini.out

echo 'Running getgrids'
$UHBD_EXEC/getgrids

while ! test -e stopnow; do
   $UHBD_EXEC/doinps; wait
   $UHBD_EXEC/$UHBD_VERS < uhbdpr.inp > uhbdpr.out
   $UHBD_EXEC/$UHBD_VERS < uhbdaa.inp > uhbdaa.out
   $UHBD_EXEC/getpots
done

/bin/cp potentials pkaS-potentials
/bin/cp sitesinpr.pdb pkaS-sitesinpr.pdb

$UHBD_EXEC/hybrid
if [ $? -ne 0 ]; then exit; fi

./cleanup.sh
