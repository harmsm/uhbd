#!/bin/sh 

delfiles[0]=stopnow
delfiles[1]=coarse.epsi*
delfiles[2]=coarse.epsj*
delfiles[3]=coarse.epsk*
delfiles[4]=howmany.dat
delfiles[5]=howmuch.dat
delfiles[6]=gridor.dat
delfiles[7]=pkaS-uhbdini.out
delfiles[8]=uhbdpr.inp
delfiles[9]=uhbdpr.out
delfiles[10]=uhbdaa.inp
delfiles[11]=uhbdaa.out
delfiles[12]=titraa.pdb
delfiles[13]=chargedaa.pdb
delfiles[14]=uhbdgen.dat
delfiles[15]=pkaS-hbuild.log
delfiles[16]=adsites.inp

i=0
while [ ${#delfiles[$i]} -gt 0 ]; do 
    /bin/rm -rf ${delfiles[$i]}
    i=`/usr/bin/expr $i + 1`
done
   
if test -e sitesinpr.pdb; then
    /bin/mv sitesinpr.pdb pkaS-sitesinpr.pdb
fi

if test -e potentials; then
    /bin/mv potentials pkaS-potentials
fi

