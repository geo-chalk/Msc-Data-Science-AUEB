library(ggplot2)
library(car)
library(gplots)
library(ggpubr)
library(psych)
library(alr4)
library(STARTS)
library(GGally)
library(AER)


######################################
#######       Exercise 1       #######
######################################
rm(list = ls())
vac = c(93, 92, 92, 89, 87, 84, 83, 83, 82, 81, 81, 81, 
        80, 76, 74, 72, 72, 69, 68, 67, 66, 64, 62, 55,
        54, 43, 29)
deaths = c(15, 10, 0, 10, 29, 4, 7, 3, 9, 7, 20, 17, 5, 
           13, 35, 69, 75, 69, 135, 113, 266, 56, 49, 
           168, 29, 267, 325)
sprintf("Check length of Vaccination vector: %s"
        ,length(vac))
sprintf("Check length of deaths vector: %s"
        , length(deaths))



# partse the data into a dataframe
df <- data.frame(vac, deaths)
colnames(df) <- c("vac", "deaths")

# Describe and summary
summary(df)
describe(df)

# histogram and boxplot for Vaccination
vac_hist <- qplot(vac,
      geom="histogram",
      binwidth = 10,  
      xlab = "Vaccination percentage",  
      fill=I("cornflowerblue"),
      col=I("lightblue"))



vac_box <- ggplot(df, 
       aes(y = vac)) +
  geom_boxplot(fill = "cornflowerblue") +
  xlab("Vaccination percentage") +
  ylab(NULL)

# histogram and boxplot for deaths
death_hist <- qplot(deaths,
        geom="histogram",
        binwidth = 50,  
        xlab = "Deaths",  
        fill=I("firebrick1"),
        col=I("tomato"))

death_box <- ggplot(df, 
       aes(y = deaths)) +
  geom_boxplot(fill = "firebrick1") +
  xlab("Deaths") +
  ylab(NULL)


# Plot histograms and boxplots
ggarrange(vac_hist, vac_box, death_hist, death_box, ncol=2, nrow=2)


# Scatter plot
ggplot(df, aes(x=vac, y=deaths)) + geom_point(size=3, color="firebrick1") +
  geom_smooth(method=lm,  linetype="dashed",
              color="darkred", fill="blue") +
  xlab("% of adult population fully Vaccinated") +
  ylab("Deaths per 1 Million population, 14-day period")


# Function to run LR and plot the corresponding  figures. 
# Navigate left and right through the figures to see the 
# Scatter plot with fitted lines
run_reg <- function(f_df) {
  # fir linear model
  fit<-lm(deaths ~ vac, data=f_df)
  print(summary(fit))
  
  #plot the linear model along with reg line
  par(mfrow=c(1, 1))
  plot(f_df$vac, f_df$deaths, 
       xlab="% of adult population fully Vaccinated", 
       ylab="Deaths per 1 Million population, 14-day period")
  abline(fit, col="red") # regression line (y~x)
  
  par(mfrow=c(2,2)) ### provide plots in a 2x2 layout
  plot(fit)
  mtext(NULL, outer=TRUE,
        line=-2, font=2, cex=1.2)
  return(fit)
}


# Create lm model to check relation of the two variables
df_fit <- run_reg(df)

# remove outliers, and run the model again
df_reduced <- df[-c(21, 25), ]
df_reduced_fit <- run_reg(df_reduced)


### Fit a quadratic model for the dataframe
df$vac2 <- df$vac^2 ### create the random variable vac^2

run_quard_reg <- function(f_df_q) {
  fit2<-lm(deaths ~ vac + vac2, data=f_df_q)
  print(summary(fit2))
  print(anova(fit2))
  par(mfrow=c(1,1))
  plot(f_df_q$vac, f_df_q$deaths, xlab="% of adult population 
     fully Vaccinated",
       ylab="Deaths per 1 Million population, 14-day period")
  abline(lm(deaths ~ vac, data=f_df_q), col="red",lwd=2) # regression line (y~x)
  lines(sort(f_df_q$vac), fitted(fit2)[order(f_df_q$vac)], col='blue',
        type='l',lwd=2,lty=2)
  legend("topright", c(expression(paste("deaths = ", alpha,
          " + ", beta, " Vacc")),expression(paste("deaths = ", alpha," + ",
          beta, " Vacc + ", gamma, ~ wt^2))), 
          lty=c(1,2),lwd=c(2,2),
          col=c("red","blue"),horiz=F)
  par(mfrow=c(2,2)) ### provide plots in a 2x2 layout
  plot(fit2)
  mtext(NULL,
        outer=TRUE, line=-2, font=2, cex=1.2)
  return(fit2)
}

# Run the function on the dataframe
df_fit2 <- run_quard_reg(df)

# remove outliers to see if the values are better
df_reduced <- df[-c(21, 25), ]
df_reduced_fit2 <- run_quard_reg(df_reduced)

anova(df_fit,df_fit2)
anova(df_reduced_fit,df_reduced_fit2)


# log transformation (adding 1 )
df_log <- df
df_log['deaths'] <- df_log['deaths'] + 1
# df_log <- log(df_log)
df_log['deaths'] <- log(df_log['deaths'])
df_log_fit <- run_reg(df_log)

# reduced
df_reduced <- df_log[-c(27), ]
df_log_fit <- run_reg(df_reduced)





######################################
#######       Exercise 2       #######
######################################
rm(list = ls())
par(mfrow=c(1,1))
attach(sleep1)
sleep1$D <- factor(sleep1$D)
sleep1$log_BodyWt <- logb(sleep1$BodyWt, 2)


### why use log 2 transformation
# Scatter plot
not_log2 <- ggplot(sleep1, aes(x=BodyWt, y=TS)) + geom_point(size=3, color="firebrick1") +
  geom_smooth(method=lm,  linetype="dashed",
              color="darkred", fill="blue") +
  xlab("Weight") + ylab(NULL)

log2 <- ggplot(sleep1, aes(x=logb(BodyWt, 2), y=TS)) + geom_point(size=3, color="firebrick1") +
  geom_smooth(method=lm,  linetype="dashed",
              color="darkred", fill="blue") +
    xlab("log2(weight)") + ylab(NULL)
  

# Create a figure by combining the different plots
figure <- ggarrange(not_log2, log2, ncol=2, nrow=1, common.legend = TRUE, labels = NULL)

# Annotate the figure by adding a common labels
annotate_figure(figure,
                left = text_grob("Total Sleep (hours/day)", rot = 90))

#  effect for danger 5
fit2<-lm(TS ~ log_BodyWt+D, sleep1, na.action=na.omit)
summary(fit2)
anova(fit2)



fit0<-lm(TS ~ 1, data=sleep1, na.action=na.omit)
fit3<-lm(TS ~ log_BodyWt*D, data=sleep1, na.action=na.omit)

summary(fit3)
anova(fit3)
anova(fit3,fit0)



par(mfrow=c(1,1))
plot(logb(BodyWt, 2), TS, type="n",ylab="Total Sleep (hours/day)",xlab=expression(paste(log[2],"(weight)")))
text(logb(BodyWt, 2)[D==1], TS[D==1],label=1,col="black")
text(logb(BodyWt, 2)[D==2], TS[D==2],label=2,col="blue")
text(logb(BodyWt, 2)[D==3], TS[D==3],label=3,col="green")
text(logb(BodyWt, 2)[D==4], TS[D==4],label=4,col="magenta")
text(logb(BodyWt, 2)[D==5], TS[D==5],label=5,col="red")
abline(fit2$coefficients[1], fit2$coefficients['log_BodyWt'], lwd=2, col="black")
abline(fit2$coefficients[1]+ fit2$coefficients[3], fit2$coefficients['log_BodyWt'], lwd=2, col="blue")
abline(fit2$coefficients[1]+ fit2$coefficients[4], fit2$coefficients['log_BodyWt'], lwd=2, col="green")
abline(fit2$coefficients[1]+ fit2$coefficients[5], fit2$coefficients['log_BodyWt'], lwd=2, col="magenta")
abline(fit2$coefficients[1]+ fit2$coefficients[6], fit2$coefficients['log_BodyWt'], lwd=2, col="red")

legend("topright", title="Specie's Danger", c("1","2","3","4","5"), 
       col=c("black","blue","green","magenta","red"),horiz=FALSE, cex=0.8, 
       fill=c("black","blue","green","magenta","red"))

######################################
#######       Exercise 3       #######
######################################
rm(list = ls())
require(starts)
data(mtcars)
head(mtcars)

# defie am, vs, cyl as factor variables
cols <- c("am", "vs", "cyl") 
mtcars[cols] <- lapply(mtcars[cols], factor)

describe(mtcars)[c(1:9)]
describe(mtcars)[c(10:13)]

# basic descriptive statistics
# Function to obtain nice plots with ggpairs
my_fn <- function(data, mapping, method="loess", ...){
  p <- ggplot(data = data, mapping = mapping) + 
    geom_point() + 
    geom_smooth(method=method, ...)
  p
}

log_mt <- subset(mtcars,  select = -c(am, vs, cyl))
log_col <- names(log_mt)
for (name in log_col){
  log_mt$name <- log2(log_mt$name)
}
# Pair plot. Commented in order to save time.  
ggpairs(log_mt, lower = list(continuous = my_fn))

# mpg, disp, hp, drat, wt, qsec, gear, carb
mpg_plot <- ggplot(mtcars, aes(x=mpg))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

disp_plot <- ggplot(mtcars, aes(x=disp))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

hp_plot <- ggplot(mtcars, aes(x=hp))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

drat_plot <- ggplot(mtcars, aes(x=drat))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

wt_plot <- ggplot(mtcars, aes(x=wt))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

qsec_plot <- ggplot(mtcars, aes(x=qsec))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

gear_plot <- ggplot(mtcars, aes(x=gear))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)

carb_plot <- ggplot(mtcars, aes(x=carb))+
  geom_density(color="darkblue", fill="cornflowerblue") +
  ylab(NULL)


# Create a figure by combining the different numerical plots
figure_3 <- ggarrange(mpg_plot, disp_plot, hp_plot, drat_plot, wt_plot, qsec_plot, 
                    gear_plot, carb_plot, ncol=4, nrow=2, 
                    common.legend = FALSE, labels = NULL) 

# Annotate the figure by adding a common labels
annotate_figure(figure_3,
                left = text_grob("Density", rot = 90))


# histogram and boxplot for Vaccination
cyl_plot <- ggplot(data=mtcars, aes(x=cyl)) + 
            geom_bar(aes(y = ..prop.., group = 1), 
            fill=I("cornflowerblue"),
            col=I("lightblue"))  +
            xlab("cyl") +
            ylab(NULL)

vs_plot <-  ggplot(data=mtcars, aes(x=vs)) + 
            geom_bar(aes(y = ..prop.., group = 1), 
            fill=I("cornflowerblue"),
            col=I("lightblue"))  +
            xlab("vs") +
            ylab(NULL)


am_plot <-  ggplot(data=mtcars, aes(x=am)) + 
            geom_bar(aes(y = ..prop.., group = 1), 
            fill=I("cornflowerblue"),
            col=I("lightblue"))  +
            xlab("am") +
            ylab(NULL)

# Create a figure by combining the different plots
figure_categorical <- ggarrange(cyl_plot, vs_plot, am_plot, ncol=3, nrow=1, 
                      common.legend = FALSE, labels = NULL) 

# Annotate the figure by adding a common labels
annotate_figure(figure_categorical,
                left = text_grob("Frequency", rot = 90))



# Automatic or manual
# Scatter plot
# plot the density for each drug
ggplot(data=mtcars, aes(x=mpg, fill=am)) + 
  geom_density(alpha = 0.4)

# plot the boxplots
ggplot(mtcars, 
       aes(x = am, 
           y = mpg)) +
  geom_boxplot(fill = "cornflowerblue") 

# 2.2
ggplot(mtcars, aes(sample = mpg, colour = am)) +
  stat_qq() +
  stat_qq_line() +
  xlab("Normal Data Quantiles") +
  ylab("Sample Quantiles")

fit_consumption <- lm(mpg ~ am, data = mtcars)
summary(fit_consumption)


# number of cylinders
# Scatter plot
# plot the density for each drug
ggplot(data=mtcars, aes(x=mpg, fill=cyl)) + 
  geom_density(alpha = 0.4)

# plot the boxplots
ggplot(mtcars, 
       aes(x = cyl, 
           y = mpg)) +
  geom_boxplot(fill = "cornflowerblue") 

# 2.2
ggplot(mtcars, aes(sample = mpg, colour = cyl)) +
  stat_qq() +
  stat_qq_line() +
  xlab("Normal Data Quantiles") +
  ylab("Sample Quantiles")

fit_consumption <- lm(mpg ~ cyl, data = mtcars)
summary(fit_consumption)


# full model
fitall_log<-lm(log2(mpg) ~ log2(disp) + log2(hp) + log2(drat)+
             + log2(wt) + log2(qsec) + cyl + vs + am +
             gear + carb, data = mtcars)
summary(fitall_log)
anova(fitall_log)

### Backward Elimination method
n <- dim(mtcars)[1]
stepBE<-step(fitall_log, scope=list(lower = ~ 1,upper= ~ log2(mpg) + log2(disp) + log2(hp) + log2(drat)+
                                  + log2(wt) + log2(qsec) + cyl + vs + am + gear + carb),
             direction="backward", data=mtcars,  k = log(n))

stepBE<-step(fitall_log, scope=list(lower = ~ 1,
                                upper= ~ log2(mpg) + log2(disp) + log2(hp) + log2(drat)+
                                  + log2(wt) + log2(qsec) + cyl + vs + am + gear + carb),
             direction="backward", data=mtcars, k = log(n))
stepBE$anova  

# full model
fitall<-lm(mpg ~ disp + hp + drat+
             + wt + qsec + cyl + vs + am + gear + carb, data = mtcars)
summary(fitall)
anova(fitall)


### Backward Elimination method
n <- dim(mtcars)[1]
stepBE<-step(fitall, scope=list(lower = ~ 1,upper= ~ log2(mpg) + log2(disp) + log2(hp) + log2(drat)+
                                  + log2(wt) + log2(qsec) + cyl + vs + am + gear + carb),
             direction="backward", data=mtcars)

stepBE<-step(fitall, scope=list(lower = ~ 1,
                                upper= ~ log2(mpg) + log2(disp) + log2(hp) + log2(drat)+
                                  + log2(wt) + log2(qsec) + cyl + vs + am + gear + carb),
             direction="backward", data=mtcars, k = log(n))



stepBE<-step(fitall, scope=list(lower = ~ 1,upper= ~ mpg + disp + hp + drat+
                                  + wt + qsec + cyl + vs + am + gear + carb),
             direction="backward", data=mtcars, , k = log(n))
stepBE$anova






######################################
#######       Exercise 4       #######
######################################
rm(list = ls())

data(HMDA)
# ?HMDA
head(HMDA)
# histogram and boxplot for Vaccination
cols <- c("deny", "phist", "selfemp", "insurance", "condomin", 
          "afam", "single", "hschool")

deny_plot <- ggplot(data=HMDA, aes(x=deny)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("deny") +
  ylab(NULL)

phist_plot <- ggplot(data=HMDA, aes(x=phist)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("phist") +
  ylab(NULL)

selfemp_plot <- ggplot(data=HMDA, aes(x=selfemp)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("selfemp") +
  ylab(NULL)

insurance_plot <- ggplot(data=HMDA, aes(x=insurance)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("insurance") +
  ylab(NULL)

condomin_plot <- ggplot(data=HMDA, aes(x=condomin)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("condomin") +
  ylab(NULL)

afam_plot <- ggplot(data=HMDA, aes(x=afam)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("afam") +
  ylab(NULL)

single_plot <- ggplot(data=HMDA, aes(x=single)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("single") +
  ylab(NULL)

hschool_plot <- ggplot(data=HMDA, aes(x=hschool)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("hschool") +
  ylab(NULL)

phist_plot <- ggplot(data=HMDA, aes(x=phist)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("phist") +
  ylab(NULL)

mhist_plot <- ggplot(data=HMDA, aes(x=mhist)) + 
  geom_bar(aes(y = ..prop.., group = 1), 
           fill=I("cornflowerblue"),
           col=I("lightblue"))  +
  xlab("mhist") +
  ylab(NULL)

# Create a figure by combining the different plots
figure_categorical <- ggarrange(deny_plot, phist_plot, selfemp_plot,
      insurance_plot, condomin_plot, afam_plot, single_plot, hschool_plot,
      phist_plot, mhist_plot, 
      ncol=5, nrow=2, common.legend = FALSE, labels = NULL) 

# Annotate the figure by adding a common labels
annotate_figure(figure_categorical,
                left = text_grob("Frequency", rot = 90))

HMDA <- subset(HMDA,  select = -c(deny, phist, selfemp, insurance, condomin, 
                                      afam, single, hschool, mhist, phist))


# basic descriptive statistics
# Function to obtain nice plots with ggpairs
my_fn <- function(data, mapping, method="loess", ...){
  p <- ggplot(data = data, mapping = mapping) + 
    geom_point() + 
    geom_smooth(method=method, ...)
  p
}

# Pair plot. Commented in order to save time.  
ggpairs(log_mt, lower = list(continuous = my_fn))







fix_vars <- function(x) {
  if (x == 'no') {
    return(0)
    } else {
      return (1)}
}

HMDA[1] <- apply(HMDA[1], 1, fix_vars)

     

HMDA$lvrat <- factor(
  ifelse(HMDA$lvrat < 0.8, "low",
         ifelse(HMDA$lvrat >= 0.8 & HMDA$lvrat <= 0.95, "medium", "high")),
  levels = c("low", "medium", "high"))
# HMDA[cols] <- lapply(HMDA[cols], factor)
HMDA$mhist <- as.numeric(HMDA$mhist)
HMDA$chist <- as.numeric(HMDA$chist)
summary(HMDA)


n <- dim(HMDA)[1]
HMDA_glm <- glm(deny~.,data = HMDA, family =poisson)
summary(HMDA_glm)
m1 <- step(HMDA_glm, direction="both")
m2 <- step(HMDA_glm, direction="both", k = log(n))

# GOF tests
with(m1, pchisq(deviance, df.residual, lower.tail = FALSE))
with(m2, pchisq(deviance, df.residual, lower.tail = FALSE))









