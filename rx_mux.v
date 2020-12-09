module rx_mux(
input clk,
input reset_n,
input [7:0] addr;
input [31:0] rx_buyprice;
input [31:0] rx_sellprice;
input [31:0] rx_buyvol;
input [31:0] rx_sellvol;
input rx_dv;

//add more as new stocks are added
output reg [7:0] addr0;
output reg [31:0] rx_buyprice0;
output reg [31:0] rx_sellprice0;
output reg [31:0] rx_buyvol0;
output reg [31:0] rx_sellvol0;
output reg rx_dv0;
);

always@(posedge clk)
begin
	if(rx_dv)
	begin
		case (addr)
		0:
		begin
			rx_buyprice0 <= rx_buyprice;
			rx_sellprice0 <= rx_sellprice;
			rx_buyvol0 <= rx_buyvol;
			rx_sellvol0 <= rx_sellvol;
			rx_dv0 <= 1;
		end
		///add more as new stocks are added
		endcase
	end
	else 
		begin
		rx_buyprice0 <= 0;
		rx_sellprice0 <= 0;
		rx_buyvol0 <= 0;
		rx_sellvol0 <= 0;
		rx_dv0 <= 0;
		end
end
endmodule