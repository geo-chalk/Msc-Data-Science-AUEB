library(ggplot2)
library(hrbrthemes)
library(bbmle)
library(car)
library(gplots)
library(agricolae)
library(dplyr)
library(ggpubr)

######################################
#######       Exercise 2       #######
######################################

# load file
filename <- './drug_response_time.txt'
df = read.table(filename, header=TRUE)
head(df, n=3)

# assign columns to Variables
time = df$time
drug = df$drug
tapply(time, drug, summary)
tapply(time, drug, describe)
describe(df)

drug_a <- subset(df, drug == 'A')
dim(drug_a)
sd(drug_a$time)

drug_b <- subset(df, drug == 'B')
dim(drug_b)
sd(drug_b$time)

# plot the density for each drug
ggplot(data=df, aes(x=time, fill=drug)) + 
  geom_density(alpha = 0.4)

# plot the boxplots
ggplot(df, 
       aes(x = drug, 
           y = time)) +
  geom_boxplot(fill = "cornflowerblue") 


 # 2.2
ggplot(df, aes(sample = time, colour = drug)) +
  stat_qq() +
  stat_qq_line() +
  xlab("Normal Data Quantiles") +
  ylab("Sample Quantiles")

# shapiro test
shapiro.test(drug_a$time)
shapiro.test(drug_b$time)



# 2.3
# drug a
norm.fit<-function(mu,sigma) { 
  -sum(dnorm(drug_a$time,mu,sigma,log=T)) }
mle.results <- mle2(norm.fit,start=list(mu=1,sigma=1),data=list(drug_a$time))
summary(mle.results)

# drug b
norm.fit<-function(mu,sigma) { 
  -sum(dnorm(drug_b$time,mu,sigma,log=T)) }
mle.results <- mle2(norm.fit,start=list(mu=1,sigma=1),data=list(drug_b$time))
summary(mle.results)



# 2.3
x1 = 3.96183
x2 = 4.074891
s1 = 0.121178
s2 = 0.107212
n1 = length(drug_a$time)
n2 = length(drug_b$time)
nu = ((s1^2/n1) + (s2^2/n2))^2/((s1^4/(n1^2*(n1-1))) 
                                + (s2^4/(n2^2*(n2-1))))

ci = c(0.05, 0.01, 0.001)

for (alpha in ci){
  t <- qt(1-alpha/2, nu)
  s <- sqrt((s1^2/n1) + (s2^2/n2))
  result <- c(x1-x2-(t*s),x1-x2+(t*s))     
  cat('result for alpha of ', 100*(1-alpha), '% is [', result[1],',',result[2],']')
  
  cat('\n')
}

for (alpha in ci){
  t <- qt(1-alpha/2, nu)
  s <- sqrt((s1^2/n1) + (s2^2/n2))
  result <- c(x1-x2-(t*s),x1-x2+(t*s))     
  cat('result for alpha of ', 100*(1-alpha))
  print(t.test(drug_a$time,drug_b$time,var.equal=TRUE,mu=0,alternative="two.sided", conf.level =  (1-alpha)))
}



######################################
#######       Exercise 4       #######
######################################
# Load the file
df2 = read.csv("./joker.csv", header=FALSE, strip.white = TRUE)
joker <- unlist(df2[1])

# plot the number freq
ggplot() + aes(x=joker, after_stat(density)) +
  geom_histogram(binwidth=1, color="lightblue", fill="royalblue3") +
  xlab("Winning Number") +
  ylab("Frequency")

# test if the numbers follow a uniform distribution
obs <- table(joker)
chisq.test(obs)

######################################
#######       Exercise 5       #######
######################################
id <- c(1:10)
before <- c(121.5,122.4,126.6,120.0,129.1,124.9,138.8,124.5,116.8,132.2)
after <- c(117.3, 128.6, 121.3, 117.2, 125.6, 121.5, 124.2, 121.6, 117.9, 125.4)
b <- rep('before', 10)
a <- rep('after', 10)
df5 <- data.frame(id = rep(id, 2), pos = c(b, a), val = c(before, after))
head(df5,4)

tapply(df5$val, df5$pos, summary)
tapply(df5$val, df5$pos, describe)
tapply(df5$val, df5$pos, sd)



ggplot(data=df5, aes(x=id, y=val, fill=pos)) +
  geom_bar(stat="identity", position=position_dodge2(reverse = TRUE))+
  geom_text(aes(label=val), vjust=1.6, color="white",
            position = position_dodge2(0.9, reverse = TRUE), size=3)+
  scale_fill_brewer(palette="Paired")+
  guides(fill = guide_legend(reverse = TRUE)) +
  theme_minimal() +
  scale_x_continuous(breaks = c(1:10)) +
  xlab("Patient id") +
  ylab("Blood Pressure")


# plot the before and after density
ggplot(data=df5, aes(x=val, fill=pos)) + 
  geom_density(alpha = 0.4) +
  guides(fill = guide_legend(reverse = TRUE)) +
  xlab("Blood Pressure") +
  ylab("Density")

# plot the boxplots, before and after
ggplot(df5, aes(x=reorder(pos, -val), y=val)) +
  geom_boxplot(fill = "cornflowerblue") +
  xlab("") +
  ylab("Blood Pressure")


#### perform t.test
d <- before - after
d
t.test(d, mu=0, alternative = "greater")




######################################
#######       Exercise 6       #######
######################################
novice <- c(22.10, 22.30, 26.20, 29.60, 31.70, 33.50, 38.90, 39.70, 43.20, 43.20)
advanced <- c(32.50, 37.10, 39.10, 40.50, 45.50, 51.30, 52.60, 55.70, 55.90, 57.70)
proficient <- c(40.10, 45.60, 51.20, 56.40, 58.10, 71.10, 74.90, 75.90, 80.30, 85.30)
names = c(rep('novice',10), rep('advanced',10), rep('proficient',10))
df6 <- data.frame(names=names, ability =c(novice, advanced, proficient))
df6$names <- factor(df6$names, levels = c("novice", "advanced", "proficient"))
head(df6)
tapply(df6$ability,df6$names, summary)
tapply(df6$ability,df6$names, sd)
tapply(df6$ability,df6$names, describe)

df6
# Density plot
ggplot(data=df6, aes(x=ability, fill=names)) + 
  geom_density(alpha = 0.4) + 
  xlab("Player Ability") +
  ylab("Density") 



# Boxplot
ggplot(df6, 
       aes(x = names, 
           y = ability)) +
  geom_boxplot(fill = "cornflowerblue") + 
  xlab('')
  ylab("Player Ability") 

  
# Anova test
fit<-aov(ability~names,data=df6)
fit
summary(fit)


### Test the normality assumption in the residuals
qqnorm(fit$residuals,main="")
qqline(fit$residuals,col="red",lty=1,lwd=2)
shapiro.test(fit$residuals)

# test Homogeneity of Variance
bartlett.test(ability~names,data=df6)
fligner.test(ability~names,data=df6)
leveneTest(ability~names,data=df6)


# Homogeneity of Variances not accepted
kruskal.test(ability~names,data=df6)



# plot the means along with a 95% CI
plotmeans(ability~names,data = df6,xlab="",
            ylab="Ability")


# pairwise test without adjusting the p-value
pairwise.t.test(df6$ability,df6$names,p.adjust.method = 'none', pool.sd = FALSE)


#more tests
TukeyHSD(fit)
pairwise.t.test(df6$ability,df6$names,p.adjust.method = 'bonferroni')
pairwise.t.test(df6$ability,df6$names,p.adjust.method = 'holm')

# LSD
DFE<-fit$df.residual
MSE<-deviance(fit)/DFE
print(LSD.test(df6$ability,df6$names,DFerror=DFE,MSerror=MSE,
               p.adj="bonferroni"))$groups


######################################
#######       Exercise 7       #######
######################################
alcohol <- c(c(rep('None', 16)), c(rep('2 pints', 16)), c(rep('4 pints', 16)))
gender <- rep(c(c(rep('Female', 8)), c(rep('Male', 8))), 3)
rating <- c(65, 70, 60, 60, 60, 55, 60, 
            55, 50, 55, 80, 65, 70, 75, 
            75, 65, 70, 65, 60, 70, 65, 
            60, 60, 50, 45, 60, 85, 65, 
            70, 70, 80, 60, 55, 65, 70, 
            55, 55, 60, 50, 50, 30, 30, 
            30, 55, 35, 20, 45, 40)
df7 <- data.frame(alcohol=alcohol, gender=gender, rating=rating)
df7$alcohol <- factor(df7$alcohol, levels = c("None", "2 pints", "4 pints"))
df7$gender <- factor(df7$gender, levels = c("Female", "Male"))


#run summary report
d_a <- distinct(df7,alcohol)
for (i in levels(unlist(d_a))){
  print(i)
  temp <- subset(df7, alcohol  == i)
  print(tapply(temp$rating,temp$gender,summary))
  print("Standard Deviation:")
  print(tapply(temp$rating,temp$gender,sd))
}

 # Density plot
females <- subset(df7, gender  == 'Female')
males <- subset(df7, gender  == 'Male')

females_plot <- ggplot(females, aes(x = rating, fill=alcohol))  + 
  geom_density(alpha = 0.4) + 
  xlab("Partner's attractiveness (Females)") +
  ylab("Density") 
males_plot <- ggplot(males, aes(x = rating, fill=alcohol))  + 
  geom_density(alpha = 0.4) + 
  xlab("Partner's attractiveness (Males)") +
  ylab("Density") 

                      
ggarrange(females_plot, males_plot, ncol=2, nrow=1, common.legend=TRUE, legend="bottom")


# Boxplot
ggplot(df7, aes(y = rating, x=gender, fill=alcohol)) +
  geom_boxplot() + 
  xlab('') +
ylab("Rating") 

attach(df7)
alcohol <- factor(alcohol, levels = c("None", "2 pints", "4 pints"))
names <- factor(names, levels = c("novice", "advanced", "proficient"))

interaction.plot(alcohol,gender,rating, type="b", col=c(1:3), leg.bty="o",
                 lwd=2, pch=c(18,24,22), trace.label="Factor Gender",
                 xlab="Factor # of Pints", ylab="Mean of Rating")


# perform Two way ANOVA
fit<-aov(rating~alcohol*gender)
fit
summary(fit)
qqnorm(fit$residuals,main=NULL)
qqline(fit$residuals,col="red",lty=1,lwd=2)
shapiro.test(fit$residuals)

# test Homogeneity of Variance
plot(fit, 1)
bartlett.test(rating~interaction(alcohol,gender))
fligner.test(rating~interaction(alcohol,gender))
leveneTest(rating~interaction(alcohol,gender))






ex4 <- matrix (nrow = 10, ncol = 3)
colnames ( ex4 ) <- c ( 'novice' , 'advanced' , 'profficient' )
ex4 [ ,1] <- c (22.1 , 22.3, 26.2, 29.6, 31.7, 33.5, 38.9, 39.7, 43.2, 43.2)
ex4 [ ,2] <- c (32.5 , 37.1, 39.1, 40.5, 45.5, 51.3, 52.6, 55.7, 55.9, 57.7)
ex4 [ ,3] <- c (40.1 , 45.6, 51.2, 56.4, 58.1, 71.1, 74.9, 75.9, 80.3, 85.3)
value <- c ( ex4 ) # convert matrix to vector
group <- rep ( colnames ( ex4 ) , each = 10)
df <- data.frame ( value , group )
# data overview
boxplot ( df$value ~ df$group )
# 1.2
# anova for test ing equal i ty of means between groups
anova1 <- aov ( value ~ group , data = df )
summary( anova1 )
lillie.test ( anova1$residuals )
shapiro.test ( anova1$residuals )
qqnorm( anova1$residuals )
qqline ( anova1$residuals )
bartlett.test(df$value ~ df$group)
