module timestamp(
input clk,
input reset_n,
input rx_dv,
input tx_dv_in, //from algorithm
output reg [31:0] tx_timestamp,
output tx_dv_out //to tx_mux
);

//when a dv comes into the system, start counter
//when a dv comes in from algo, stop counter, send assign counter value to an output, send dv out
reg [31:0] counter;
reg [3:0] state;

always@(posedge clk)
begin
	case (state)
	0:
	begin
		if(rx_dv) state <= 1;
		else 
		begin
			state <= 0;
			counter <= 0;
			tx_dv_out <= 0;
		end
	end
	1:
	begin
		if(tx_dv_in)
		begin
			state <= 0;
			tx_timestamp <= counter;
			tx_dv_out <= 1;
		end
		else counter <= counter + 1;
	end
	endcase
end



endmodule