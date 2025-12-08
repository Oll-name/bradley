#include <iostream>
#include <fstream>
#include "SCServo.h"

SMS_STS sm_st;

int main(int argc, char **argv)
{
	if(argc<2){
        std::cout<<"argc error!"<<std::endl;
        return 0;
	}
	std::cout<<"serial:"<<argv[1]<<std::endl;
    if(!sm_st.begin(115200, argv[1])){
        std::cout<<"Failed to init sms/sts motor!"<<std::endl;
        return 0;
    }

	//csv file
	fstream fout;
	fout.open("test1.csv", ios::out | ios::app);



	sm_st.WritePosEx(1, 4095, 2400, 50); // Start position
	usleep(2187*1000);//[(P1-P0)/V]*1000+[V/(A*100)]*1000
	int Pos;
	int Speed;		
	int Load;
	int Time = 0;
	while(1){
		sm_st.WritePosEx(1, 4095, 2400, 50); // end position
		Pos = sm_st.ReadPos(1);
		Speed = sm_st.ReadSpeed(1);
		Load = sm_st.ReadLoad(1);	
		fout << Time << ", "
             << Load << ", "
             << Pos << ", "
             << Speed 
			 << "\n";
		usleep(1000);
		++Time;


		
		

	}
}
