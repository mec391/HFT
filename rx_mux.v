module rx_mux(
input clk,
input reset_n,

//from uart (rx):
input [7:0] addr,
input [31:0] rx_buyprice,
input [31:0] rx_sellprice,
input [31:0] rx_buyvol,
input [31:0] rx_sellvol,
input rx_dv,

//to system0:
output reg [7:0] addr0,
output reg [31:0] rx_buyprice0,
output reg [31:0] rx_sellprice0,
output reg [31:0] rx_buyvol0,
output reg [31:0] rx_sellvol0,
output reg rx_dv0
//add more as new stocks are added
);
reg [3:0] sm;
always@(posedge clk)
begin
	case (sm)
	0:
	begin
		if(rx_dv) 
		begin
			case(addr)
			0:
			begin
			rx_buyprice0 <= rx_buyprice;
			rx_sellprice0 <= rx_sellprice;
			rx_buyvol0 <= rx_buyvol;
			rx_sellvol0 <= rx_sellvol;
			rx_dv0 <= 1;
			sm <= 1;
			end
			endcase
			//add more addr cases if more stocks are added
		end
		else
		begin
			sm <= 1; //crossing clock domains so add delay to prevent triggering dv twice
		end
	end
	1:
	begin
		sm <= 2; //more delay
		rx_buyprice0 <= 0;
		rx_sellprice0 <= 0;
		rx_buyvol0 <= 0;
		rx_sellvol0 <= 0;
		rx_dv0 <= 0;
	end
	2:
	begin
		sm <= 0; //more delay
	end
	endcase
end
endmodule