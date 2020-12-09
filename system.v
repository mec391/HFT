module system(
input clk,
input reset_n,

input [7:0] addr0; 
input [31:0] rx_buyprice0;
input [31:0] rx_sellprice0;
input [31:0] rx_buyvol0;
input [31:0] rx_sellvol0;
input rx_dv0;

output reg [7:0] tx_addr0;
output reg [7:0] tx_buysell0;
output reg [31:0] tx_timestamp0;
output tx_dv0;

);



///for now just route input data directly to output mux for loopback testing



		//FOR ADDR 0:
		//instantiate DP-BRAM (Book Handler)
		//instantiate MA algo
		//instantiate NN1 algo
		//instantiate NN2 algo
		//instantiate decision-making module
		//instantiate timestamp
endmodule