library(ggplot2)

# call_duration_100.txt
filename <- './call_duration_100.txt'
a <- 2 ### parameter alpha
b <- 1 ### parameter beta
x = read.table(filename)$x
length(x)

# Q1
hist(x, 50, freq = FALSE, xlab = "Duration", main=paste("Histogram of x for", substr(filename, 3, 50), sep=" "))
xSeq <- seq(min(x),max(x), length = 1000)
points(xSeq, dgamma(xSeq, a, scale=b), type = "l", col = "red", lwd = 2)
legend("topright",inset = 0.05, max(dgamma(xSeq, a, scale=b)), lty = 1, col = 2, bty = "n", legend=bquote(italic(f)*"("*italic(x)*") = "
                                                               *italic(x)*italic(e)^{- italic(x)}*", x">=0))

myfun <- function(x) {
  if(x<=3){ return(2)
  } else {
    return(2+6*(x-3))
  }
}

# Q2
n <- length(x)
# (a) P(call lasts at most one minute.) 
sum((x <= 1)*1)/n
# (b) P(call lasts at least two minutes).
sum((x >= 2)*1)/n
# (c) Mean and Variance of call duration.
mean(x)
var(x)
# (d)Cost of a call with average duration.
lapply(mean(x), FUN = myfun)
# (e) Average cost of a call.
sum(unlist(lapply(x, FUN = myfun)))/n
# (f) 1st and 3rd quartile of call duration.
quantile(x, prob = c(1/4,3/4))

rm(list=ls()) 



# call_duration_10000.txt
filename <- './call_duration_10000.txt'
a <- 2 ### parameter alpha
b <- 1 ### parameter beta
x = read.table(filename)$x
length(x)

# Q1
hist(x, 50, freq = FALSE, xlab = "Duration", main=paste("Histogram of x for", substr(filename, 3, 50), sep=" "))
xSeq <- seq(min(x),max(x), length = 1000)
points(xSeq, dgamma(xSeq, a, scale=b), type = "l", col = "red", lwd = 2)
legend("topright",inset = 0.05, max(dgamma(xSeq, a, scale=b)), lty = 1, col = 2, bty = "n", legend=bquote(italic(f)*"("*italic(x)*") = "
                                                                                                          *italic(x)*italic(e)^{- italic(x)}*", x">=0))

myfun <- function(x) {
  if(x<=3){ return(2)
  } else {
    return(2+6*(x-3))
  }
}

# Q2
n <- length(x)
# (a) P(call lasts at most one minute.) 
sum((x <= 1)*1)/n
# (b) P(call lasts at least two minutes).
sum((x >= 2)*1)/n
# (c) Mean and Variance of call duration.
mean(x)
var(x)
# (d)Cost of a call with average duration.
lapply(mean(x), FUN = myfun)
# (e) Average cost of a call.
sum(unlist(lapply(x, FUN = myfun)))/n
# (f) 1st and 3rd quartile of call duration.
quantile(x, prob = c(1/4,3/4))

rm(list=ls()) 
