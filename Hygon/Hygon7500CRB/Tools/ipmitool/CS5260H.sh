#!/bin/bash

#/*
#Copyright (c) 2019 - 2020 BYOSoft Corporation. All rights
#reserved.<BR> This software and associated documentation (if
#any) is furnished under a license and may only be used or copied
#in accordance with the terms of the license. Except as permitted
#by such license, no part of this software or documentation may
#be reproduced, stored in a retrieval system, or transmitted in
#any form or by any means without the express written consent of
#BYOSoft Corporation.
#
#**/

#
#Author: wanjunjie@byosoft.com.cn
#


DisplayUsage()
{
	echo "----------------------------------------------------------"
	echo " "
	echo "Usage: ./CS5260H_Standard_20201204.sh <Target> <IP> <UserName> <PassWord> <FileName>"
	echo " "
	echo "Target: BMC / BACKUP_BMC / BIOS / CPLD"
	echo " "
	echo "Eg. ./CS5260H_Standard_20201204.sh BMC 192.168.15.3 admin admin openbmc.mtd.tar"
	echo "    ./CS5260H_Standard_20201204.sh BACKUP_BMC 192.168.15.3 admin admin openbmc.mtd.tar"
	echo "    ./CS5260H_Standard_20201204.sh BIOS 192.168.15.3 admin admin bios.bin"
	echo "    ./CS5260H_Standard_20201204.sh CPLD 192.168.15.3 admin admin CPLD.aje"
	echo " "
	echo "----------------------------------------------------------"
}

DisplayFailed()
{
	echo ""
	echo "############################################"
	echo ">>>>                                    <<<<"
	echo ">>>>   ******     *      ***    *       <<<<"
	echo ">>>>   *         * *      *     *       <<<<"
	echo ">>>>   ******   *   *     *     *       <<<<"
	echo ">>>>   *       *******    *     *       <<<<"
	echo ">>>>   *       *     *    *     *       <<<<"
	echo ">>>>   *       *     *   ***    *****   <<<<"
	echo ">>>>                                    <<<<"
	echo "############################################"
	echo ""
}

if [ T$1 == T"" ]
then
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

if [ T$2 == T"" ]
then
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

if [ T$3 == T"" ]
then
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

if [ T$4 == T"" ]
then
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

if [ T$5 == T"" ]
then
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

TARGET=$1
BMCIP=$2
USERNAME=$3
PASSWORD=$4
UPDATEFILE=$5

case "$1" in
"?" | "h" | "H")
DisplayUsage
exit 1
;;
*)
if [ "$TARGET" == "BMC" -o "$TARGET" == "BACKUP_BMC" -o "$TARGET" == "BIOS" -o "$TARGET" == "CPLD" ]
then
	echo "Do you make sure you want to flash $TARGET Y/N:"
	keyinput="null"
	while [ $keyinput == "null" ]
	do
	read keyinput
	sleep 1
	if [ $keyinput == "Y" -o $keyinput == "y" ]
	then
		echo "Starting flash $TARGET:"
	else
		exit 1
	fi
	done
else
	echo "Invalid Parameter!"
	DisplayUsage
	exit 1
fi

./loquat -d $TARGET -i redfish -f $UPDATEFILE -h $BMCIP -u $USERNAME -p $PASSWORD

FlashStatus=$(cat fail_status)

if [ "$FlashStatus"x == "1000"x ];then
	case "$TARGET" in
	"BMC")
		echo ""
		echo "############################################"
		echo ">>>>>>        BMC Flash Success!      <<<<<<"
		echo "############################################"
		echo ""
		exit 0
	;;
	"BACKUP_BMC")
		echo ""
		echo "############################################"
		echo ">>>>>>   BACKUP_BMC Flash Success!    <<<<<<"
		echo "############################################"
		echo ""
		exit 0
	;;
	"BIOS")
		echo ""
		echo "############################################"
		echo ">>>>>>       BIOS Flash Success!      <<<<<<"
		echo "############################################"
		echo ""
		exit 0
	;;
	"CPLD")
		echo ""
		echo "############################################"
		echo ">>>>>>       CPLD Flash Success!      <<<<<<"
		echo "############################################"
		echo ""
		exit 0
	;;
	esac
else
	case "$FlashStatus" in
	"1001")
	echo ""
	echo "############################################"
	echo ">>>>     BMC Server Connect Failed      <<<<"
	echo ">>>>    Please Check BMC IP Validity    <<<<"
	echo "############################################"	
	;;
	"1002")
	echo ""
	echo "############################################"
	echo ">>>>       Get RespHeader Failed        <<<<"
	echo "############################################"	
	;;
	"1003")
	echo ""
	echo "############################################"
	echo ">>>>         Upload File Failed         <<<<"
	echo "############################################"	
	;;
	"1004")
	echo ""
	echo "############################################"
	echo ">>>>     Prepare For Update Failed      <<<<"
	echo "############################################"	
	;;
	"1005")
	echo ""
	echo "############################################"
	echo ">>>>         IMAGE IS INVALID           <<<<"
	echo "############################################"	
	;;
	"1006")
	echo ""
	echo "############################################"
	echo ">>>>      Get Verify Status Failed      <<<<"
	echo "############################################"	
	;;
	"1007")
	echo ""
	echo "############################################"
	echo ">>>>     Check Image Valid Timeout      <<<<"
	echo "############################################"	
	;;
	"1008")
	echo ""
	echo "############################################"
	echo ">>>>     Check Image Valid Failed       <<<<"
	echo "############################################"	
	;;
	"1009")
	echo ""
	echo "############################################"
	echo ">>>>       Get Erase Status Failed      <<<<"
	echo "############################################"	
	;;
	"1010")
	echo ""
	echo "############################################"
	echo ">>>>      Firmware Update Timeout       <<<<"
	echo "############################################"	
	;;
	*)
	;;
	esac
	DisplayFailed
fi

exit 1
;;
esac