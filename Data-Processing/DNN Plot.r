library(plotly)
setwd("/Users/Heran/Documents/CME/Apr\ 15th/time\ series")
p <- read.csv("prediction.csv", header = TRUE)
trade <- read.csv("timeseries.csv", header = TRUE)
es <- read.csv("esOrderWholeDay.csv", header = TRUE)
tp <- es$trade_price
tp2 <-c(tp[1])
for (i in 1:(length(tp)-1)){
  if (tp[i+1] != tp[i]){
    tp2 <- c(tp2, c(tp[i+1]))
  }
}

acc <- p$accuracy
vol <- trade$vol
ay <- list(tickfont = list(color = "red"), overlaying = "y", side = "right")
plot_ly(x=1:56989, y=tp2, name = "Trade Price")%>%
  # add_trace(x=1:56989, y = acc, name = "Accuracy", yaxis = "y2")%>%
  # add_trace(x=1:56989, y = vol, name = "Volatility", yaxis = "y2")%>%
  layout(title = "E-mini", yaxis2 = ay, 
         shapes = list(list(type = "rect", 
         fillcolor = "blue", line = list(color = "blue"), opacity = 0.1, 
         x0 = 45591.2, x1 = 56989,
         y0 = 197000, y1 = 201500)))



