module system(
input clk,
input reset_n,

//from rx_mux:
input [7:0] addr0, 
input [31:0] rx_buyprice0,
input [31:0] rx_sellprice0,
input [31:0] rx_buyvol0,
input [31:0] rx_sellvol0,
input rx_dv0,

//to tx_mux:
output reg [7:0] tx_addr0,
output reg [7:0] tx_buysell0,
output  [31:0] tx_timestamp0,
output  tx_dv0

);

reg [31:0] regged_buyprice;
reg [3:0] counter;
reg loopback_test;
///for now just route input data directly to output mux for loopback testing -- the following is just for loopback testing
always@(posedge clk)
begin

tx_addr0 <= 0;

	case (counter)
	0:
	begin
		if(rx_dv0)
		begin
			counter <= 1;
			if(rx_buyprice0 == 32'b00000100110100101000000000000000) tx_buysell0 <= 2;
			else tx_buysell0 <= 0;
		end
		else
		begin
			counter <= 0;
			tx_buysell0 <= 0;
		end
	end
	1:
	begin
		loopback_test <= 1;
		counter <= 2;
	end
	2:
	begin
	loopback_test <= 0;
		if(tx_dv0)
		begin
			counter <= 0;
		end
	end
	endcase
end



		//FOR ADDR 0:
		//instantiate DP-BRAM (Book Handler)
		//instantiate MA algo
		//instantiate NN1 algo
		//instantiate NN2 algo
		//instantiate decision-making module

//instantiate timestamp
timestamp ts0(
.clk (clk),
.reset_n (reset_n),
.rx_dv (rx_dv0),
.tx_dv_in (loopback_test), //from algorithm
.tx_timestamp (tx_timestamp0),
.tx_dv_out (tx_dv0)//to tx_mux
	);
endmodule