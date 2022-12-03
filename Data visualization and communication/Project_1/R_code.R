library(dplyr)
library(ggplot2)
library(ggExtra)
library(shadowtext)
library(cartography)
library(reshape)
library(patchwork)
library(hrbrthemes)
library(devtools)
library(ggpubr)
# install_github("wilkox/treemapify")
library(treemapify)
library(tidyverse)
library(reshape2)
library(waffle)
library(cowplot)
library('modelsummary')
library('cowplot')
library("magick")


#### Load Data ####
df_temp <- read.csv(file='./data/tps00122_linear.csv')
names(df_temp) <- c('age', 'sex', 'geo', 'year', 'suicide_rate')
head(df_temp)

# Country Codes
codes <- read.csv(file='./data/Country_codes.csv', header=FALSE)
names(codes) <- c('geo', 'country')
head(codes)

df <- left_join(df_temp, codes, by='geo')
df$suicide_rate <- as.numeric(as.character(df$suicide_rate))
df$year <- as.factor(df$year)
df$geo <- as.character(df$geo)
head(df)


# 2019 data ----

# read 2019 data
df_comp <- read.csv(file='./data/data.csv')
df_2019 <- df_comp[df_comp$Indicator.Name == 'Suicide mortality rate (per 100,000 population)' ,c('Country.Name' ,'Country.Code', 'Indicator.Name', 'X2019')]
names(df_2019)<- c('region', 'abrv', 'indicator', 'suicide_rate')

# Map ====

# join with polygons
world <- map_data("world")
world_data <- left_join(world, df_2019, by='region')
temp_map = world_data[world_data$region %in% unique(df_2019$region), ]
centroid <- aggregate(cbind(long,lat) ~ abrv + suicide_rate, data=temp_map, FUN=mean)


ggplot(world_data) +
  geom_polygon(data=subset(world_data, !is.na(suicide_rate)),
               aes(long, lat, group=group, fill = suicide_rate), color='black', size=0.01) +
  geom_polygon(data=subset(world_data, is.na(suicide_rate)),
               aes(long, lat, group=group), fill='gray', color='black', size=0.01, alpha=1) +
  coord_quickmap() +
  scale_fill_distiller('Suicide Rate', palette = "YlOrBr", direction= 1, na.value = "grey") +
  theme_void() +
  coord_cartesian(
    xlim = c(min(temp_map$long), max(temp_map$long)), 
    ylim = c(min(temp_map$lat), max(temp_map$lat))) + 
  geom_shadowtext(aes(label=abrv, x=long, y=lat), data=centroid,  
                  size=3, hjust=0.5) +
  ggtitle('Suicide mortality rate* in the EU (2019)') + 
  labs(caption=expression(paste('*per 100,000 population'))) +
  theme(legend.position='right',
        legend.text=element_text(12),
        legend.title=element_text(size=14),
        legend.key.size = unit(1,'line'),
        plot.title=element_text(size=18, hjust=0.5),
        panel.background = element_rect(fill = "#D4F1F4"),
        plot.caption =  element_text(hjust = 0.02)) 


# barplot ====
temp <- df_2019[!df_2019$region %in% c('European Union', 'Euro area'), ]
temp$isgreece <- with(temp, ifelse(region == "Greece", '#3b5998', '#ffd7b5'))

ggplot(temp,  aes(x = reorder(region, suicide_rate), y = suicide_rate)) +
  geom_bar(stat = "identity", fill= temp$isgreece) +
  geom_hline(aes(yintercept = mean(suicide_rate), color = "EU mean"), linetype = 1, size = 1) + 
  scale_colour_manual(values = c("red", "blue")) +
  geom_text(aes(label=suicide_rate), hjust=1.1, color= ifelse(temp$isgreece == "#3b5998", 'white', 'black'), size=3.5, fontface = "bold") +
  coord_flip() + 
  ggtitle('Suicide mortality rate* in the EU (2019)') +
  labs(x = "Country",
       y = "Suicide Rate",
       color = NULL)+
  theme_minimal() + 
  labs(caption=expression(paste('*per 100,000 population'))) +
  theme(legend.position='right',
        legend.title=element_blank(),
        legend.key.size=unit(2,'line'),
        legend.text=element_text(size=16),
        axis.text=element_text(size=15),
        axis.title=element_text(size=16),
        plot.title=element_text(size=19, hjust=0.02),
        plot.caption =  element_text(hjust = 0.02))








# causes of death Treemap ====
df_causes <- read.csv(file='./data/causes_of_death.csv')
head(df_causes)

df_causes_code <- read.csv(file='./data/causes_of_death_mapping.csv')
head(df_causes_code)

temp_causes <- left_join(df_causes, df_causes_code, by='icd10')
temp_causes <- temp_causes %>% filter(!is.na(Cause.of.death))
temp_causes$age[temp_causes$age == "Y_GE65"] <- "Over 65"
temp_causes$age[temp_causes$age == "Y_LT65"] <- "Under 65"
temp_causes <- temp_causes[,c("sex", "age", "geo", "TIME_PERIOD", "OBS_VALUE", "Cause.of.death")]
names(temp_causes) <- c("sex", "age", "geo", "year", "value", "cause")
head(temp_causes)

df_causes_2019 <- subset(temp_causes, year == '2019' & age != 'TOTAL' & geo == "EL",
                            select=c('sex' ,'age', 'value', "cause"))
df_causes_2019$age[df_causes_2019$age == "Y_GE65"] <- "Over 65"
df_causes_2019$age[df_causes_2019$age == "Y_LT65"] <- "Under 65"
df_causes_2019 <- aggregate(value ~ sex + age + cause, data=df_causes_2019, FUN=sum)
head(df_causes_2019)


df_causes_2019$cause <- as.factor(df_causes_2019$cause)
df_causes_2019$value <- as.numeric(df_causes_2019$value)
head(df_causes_2019)


treemap <- ggplot(df_causes_2019, aes(area=value, label=cause,  fill = cause)) +
  facet_grid(rows=vars(sex), cols=vars(age)) +
  geom_treemap() +
  geom_treemap_text(
    colour = "black",
    place = "centre",
    reflow=TRUE, 
    alpha=0.5) +
  scale_fill_brewer("Cause of Death", palette = "Spectral" ) +
  theme(plot.margin=unit(c(0,0.2,0.14,12.1),"cm"),
    legend.position=c(-0.42,0.8),
        legend.text=element_text(size=15),
        legend.title=element_text(size=18),
        plot.title = element_text(hjust=0.5, size=20),
        axis.title=element_text(size=20),
        axis.text=element_text(size=10),
        axis.text.x=element_text(angle=60, vjust=0.6),
        strip.text = element_text(size=13),
        plot.caption =  element_text(hjust = 0.02)) +
  ggtitle('Causes of death per gender and age group')
  
zoom <- ggplot(df_causes_2019,  aes(x = age, y = value)) +
  geom_bar(stat = "identity", fill="#D2B4DE") +
  labs(x = "Age group",
       y = "Number of deaths",
       color = NULL)+
  theme(plot.title = element_text(size=13),
        axis.title=element_text(size=12),
        axis.text=element_text(size=7),
        strip.text = element_text(size=13)) +
  ggtitle('Total Number of deaths per age group')


ggdraw() +
  draw_plot(treemap) +
  draw_plot(zoom, x = 0.0, y = 0.05, width = .35, height = .4) +
  ggtitle('Causes of death per gender and age group') +
  geom_rect(aes(xmin=0.445,xmax=0.995,ymin=0.005,ymax=0.305), colour="black", fill=NA, size=1) + 
  geom_segment(aes(x=0.445, y = 0.1625, xend =0.36, yend =  0.405)) +
  geom_segment(aes(x=0.445, y = 0.1625, xend =0.36, yend =  0.15)) +
  geom_rect(aes(xmin=0.005,xmax=0.36,ymin=0.05,ymax=0.5), colour="black", fill=NA, size=1)


# historical data - Greece (M, F) ====
temp_T <- subset(df, sex=='T' & geo == 'EL')
temp_M <- subset(df, sex=='M' & geo == 'EL')
temp_F <- subset(df, sex=='F' & geo == 'EL')
temp_E <- subset(df, sex=='T' & geo == 'EU27_2020')
temp_T$year <- as.factor(temp_T$year)
temp_M$year <- as.factor(temp_M$year)
temp_F$year <- as.factor(temp_F$year)
temp_E$year <- as.factor(temp_E$year)

newData <- melt(list(df1 = temp_T, df2 = temp_M, df3 = temp_F, df4 = temp_E), 
                id.vars = "year", measure.vars = 'suicide_rate')
cols <- c("green", "darkblue", "pink", "gray")
newData$year <- as.factor(newData$year)

ggplot(newData, aes(year, value)) + 
  geom_line(aes(color = L1, group = L1),  size=1.2) + 
  scale_colour_manual(name = '', 
                      values =c('df1' ='red', 'df2' = 'blue', 'df3' = 'orange', 'df4' = 'black'), 
                      labels = c('Total', 'Male', 'Female', "Europe Average")) +
  labs(x='Year', y='Suicide Rate', caption=expression(paste('*per 100,000 population'))) +
  theme(legend.position='right',
        legend.text=element_text(size=12),
        plot.title = element_text(hjust=0.5, size=23),
        axis.title=element_text(size=20),
        axis.text=element_text(size=10),
        strip.text = element_text(size=13),
        plot.caption =  element_text(hjust = 0.02)) +
  ggtitle('Suicide mortality rate* (2011-2019)\n Greece vs Europe ')







# historical data - Greece ====
df_comp <- read.csv(file='./data/data.csv',  check.names=FALSE)
melted_df <- melt(df_comp, id.vars = c("Country Name", "Country Code", "Region", "Indicator Name", "IncomeGroup"))
names(melted_df) <- c("country", "code", "region", "indicator", "income", "year", "suicide_rate")
head(melted_df)

temp_T <- subset(melted_df, code == 'GRC' & indicator == 'Suicide mortality rate (per 100,000 population)')
temp_E <- subset(melted_df, code == 'EMU' & indicator == 'Suicide mortality rate (per 100,000 population)')
temp_T$year <- as.factor(temp_T$year)
temp_E$year <- as.factor(temp_E$year)

coeff <- 5

ggplot(temp_T, aes(year, suicide_rate, group=1, color='GR')) + 
  geom_line( size=1.2) + 
  geom_smooth( aes(color="smooth1"), method = "lm", se = FALSE, linetype = "dashed", alpha = .15) +
  geom_line(temp_E, mapping=aes(year, suicide_rate, color='EU'),  size=1.2) + 
  geom_smooth(temp_E, mapping=aes(year, suicide_rate), color="#EF7C8E", alpha = .15 , method = "lm", se = FALSE, linetype = "dashed") +
  scale_y_continuous(
    n.breaks=6,
    # Add a second axis and specify its features
    sec.axis = sec_axis( trans=~., name="Suicide Rate (Europe)")
  ) + 
  scale_colour_manual(name = '', 
                      values =c('GR' ='#619CFF', 'EU' = '#69b3a2', "smooth1" = "#EF7C8E"), 
                      labels = c('Greece', "Europe Average", "Regression Line(s)")) + 
  labs(x='Year', y='Suicide Rate (Greece)', caption=expression(paste('*per 100,000 population'))) +
  theme(legend.position='top',
        legend.text=element_text(size=12),
        plot.title = element_text(hjust=0.5, size=23),
        axis.title=element_text(size=20),
        axis.text.x =element_text(angle=60, vjust=0.6, size=15),
        axis.text.y =element_text(size=13),
        strip.text = element_text(size=15),
        plot.caption =  element_text(hjust = 0.02),
        axis.title.y = element_text(color = "#619CFF"),
        axis.title.y.right = element_text(color = '#69b3a2'),
        panel.background = element_rect(fill = "#F1F1F0")) +
  ggtitle('Suicide mortality rate* (2000-2019)\n Greece vs Europe ') 





# historical data total ====
temp <- subset(melted_df, region == 'Europe' & indicator == 'Suicide mortality rate (per 100,000 population)')

ggplot(temp, aes(x=year, y=suicide_rate, group=country)) +
  theme_gray() +
  geom_line(size=1, color='#619CFF') +
  facet_wrap(~country) +
  scale_x_discrete(labels= c("2000", '', '2002', "", '2004', '', '2006', '', '2008', '', '2010',
                             '', '2012', '', '2014', '', '2016', '', '', '2019')) +
  scale_y_continuous(n.breaks=4) + 
  labs(x='Year', y='Suicide Rate', caption=expression(paste('*per 100,000 population'))) +
  theme(legend.position=c(0.85,0.05),
        legend.text=element_text(size=15),
        plot.title = element_text(hjust=0.5, size=20, face = "bold"),
        axis.title=element_text(size=20),
        axis.text=element_text(size=10),
        axis.text.x=element_text(angle=60, vjust=0.6),
        strip.text = element_text(size=13),
        plot.caption =  element_text(hjust = 0.02)) +
  ggtitle('Suicide mortality rate* in Europe (2000-2019)')


# historical data rate vs   ====
temp_1 <- subset(melted_df, country == 'Greece' & indicator == 'Suicide mortality rate (per 100,000 population)')
temp_2 <- subset(melted_df, country == 'Greece' & indicator == 'Percentage of gross domestic product (GDP)')

ggplot() + 
  geom_bar(data=temp_2, mapping=aes(x=year, y=suicide_rate/20, color='GDPR'), 
           stat="identity",  fill = "#EF7C8E") +
  geom_line(data=temp_1, aes(year, suicide_rate, group=1, color='rate'), size=2) +
  scale_y_continuous(
    # Add a second axis and specify its features
    sec.axis = sec_axis( trans=~.*20, name="Percentage of gross domestic product (GDP)")
  ) + 
  scale_colour_manual(name = '', 
                      values =c('rate' ='#619CFF', "GDPR" = "#EF7C8E"), 
                      labels = c("Percentage of GDP", "Suicide Rate"))+
  labs(x='Year', y='Suicide Rate (Greece)', caption=expression(paste('*per 100,000 population'))) + 
  theme(legend.position='top',
        legend.text=element_text(size=12),
        plot.title = element_text(hjust=0.5, size=23),
        axis.title=element_text(size=20),
        axis.text.x =element_text(angle=60, vjust=0.6, size=15),
        axis.text.y =element_text(size=13),
        strip.text = element_text(size=15),
        plot.caption =  element_text(hjust = 0.02),
        axis.title.y = element_text(color = "#619CFF"),
        axis.title.y.right = element_text(color = '#EF7C8E'),
        panel.background = element_rect(fill = "#F1F1F0")) +
  ggtitle('Suicide mortality rate* vs GDP in Greece (2000-2019)') 

# test correlation ====
library("ggpubr")

ggscatter(x = temp_1$suicide_rate, y = temp_2$suicide_rate, 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Miles/(US) gallon", ylab = "Weight (1000 lbs)")



# diff between sex ====

plot1 <- ggplot(data=subset(temp_causes, sex!='Total' & age!='TOTAL' &
                       geo != 'EU27_2020' & geo != 'EU28' &
                       nchar(geo) ==2), aes(x=age, y=value, fill=sex)) + 
  theme_bw() +
  geom_point(position=position_jitterdodge(0.1), aes(col=sex), alpha=0.2) +
  stat_boxplot(geom='errorbar', linetype=1) +
  geom_boxplot(alpha=0.6,
               outlier.colour="black",
               outlier.fill="black",
               outlier.shape = NA)  +
  scale_y_continuous(limits = quantile(temp_causes$value, c(0.1, 0.99))) +
  theme(legend.position="none",
        legend.title=element_blank(),
        legend.key.size=unit(2,'line'),
        legend.text=element_text(size=16),
        axis.text=element_text(size=15, hjust=0.5),
        axis.title=element_text(size=15),
        plot.title=element_text(size=20, hjust=1)) +
  geom_rect(aes(xmin=1.6,xmax=2.4,ymin=-20,ymax=30), colour="black", fill=NA) + 
  geom_segment(aes(x=2, y = 30, xend =2.57, yend = 255)) +
  geom_segment(aes(x=2, y = 30, xend =1.9, yend = 255)) + ylab('Suicide Rate') +
  xlab('Age') +  scale_fill_viridis_d() + viridis::scale_color_viridis(discrete = TRUE)
  

plot2 <- ggplot(data=subset(temp_causes, sex!='Total' & age!='TOTAL' &
                     geo == 'EL' &
                     nchar(geo) ==2), aes(x=age, y=value, fill=sex)) + 
  theme_bw() +
  geom_point(position=position_jitterdodge(0.1), aes(col=sex), alpha=0.2) +
  stat_boxplot(geom='errorbar', linetype=1) +
  geom_boxplot(alpha=0.6,
               outlier.colour="black",
               outlier.fill="black",
               outlier.shape = NA)  +
  scale_y_continuous(limits = quantile(temp_causes$value, c(0.1, 0.95))) +
  geom_rect(aes(xmin=1.6,xmax=2.4,ymin=-20,ymax=30), colour="black", fill=NA) + 
  geom_segment(aes(x=2, y = 30, xend =2.57, yend = 255)) +
  geom_segment(aes(x=2, y = 30, xend =1.9, yend = 255)) + ylab('') + xlab('Age') +
  scale_fill_viridis_d() +  viridis::scale_color_viridis(discrete = TRUE)

plot1 + plot2 +
  ggtitle('Suicide mortality rate in Europe (left) and Greece (right) (gender and age split)') + 
theme(legend.position='right',
      legend.title=element_blank(),
      legend.key.size=unit(2,'line'),
      legend.text=element_text(size=16),
      axis.text=element_text(size=15, hjust=0.5),
      axis.title=element_text(size=15),
      plot.title=element_text(size=18, hjust=0.9)) 



# density ====
# Change density plot fill colors by groups
ggplot(data=subset(temp_causes, geo != 'EU27_2020' & geo != 'EU28' & age != "TOTAL" &
                     nchar(geo) ==2 & cause == "Suicide" & year %in% c(2011, 2019)), aes(x=value, fill=age)) +
  geom_density(alpha=0.4) +
  coord_cartesian(xlim = quantile(temp_causes$value, c(00, 0.93))) +
  geom_vline(data=subset(temp_causes, geo == 'EL' 
                         & cause == "Suicide" 
                         & year %in% c(2011, 2019)
                         & age != "TOTAL"), mapping=aes(xintercept = value, color=age), size=1 ) +
  scale_fill_brewer(palette="Dark2")+
  facet_grid(year ~ sex)+
  labs(title='Suicide Rate 2011 vs 2019 per sex over two age groups \nin Europe (density) and Greece (lines)',
       x='Suicide Rate',
       y='Density') +
  theme(legend.title=element_text("Age", size=20),
        legend.text=element_text(size=15),
        legend.key.size=unit(1.5, 'line'),
        plot.title=element_text(size=21, hjust = 0.5),
        axis.title=element_text(size=17),
        axis.text=element_text(size=13),
        strip.text=element_text(size=15),
        strip.background=element_rect(fill='#F3F3F3'))



# GDP & rate ====
temp_1 <- subset(melted_df, region == 'Europe' & indicator == 'Suicide mortality rate (per 100,000 population)')
temp_2 <- subset(melted_df, region == 'Europe' & indicator == 'Percentage of gross domestic product (GDP)')

temp <- left_join(temp_1, temp_2, by=c("country", "code", "region", "year"))
temp


mod = lm(suicide_rate.y ~ suicide_rate.x, temp)
modelsummary(mod, output = "table.png")

p <- ggplot(subset(temp, region == 'Europe'), 
       aes(x=suicide_rate.y, y=suicide_rate.x)) +
  theme_bw() +
  geom_point(color="#69b3a2", size=2) +
  stat_smooth(method = "lm", col = "black", alpha=0.15, size=1) +
  labs(title='Suicide Rates and \nPercentage of gross domestic product (GDP)',
       x='Percentage of gross domestic product (GDP)',
       y='Suicide mortality rate (per 100,000 population)')+
  theme(legend.key.size=unit(1.5, 'line'),
        plot.title=element_text(size=21, hjust = 0.5),
        axis.title=element_text(size=14),
        axis.text=element_text(size=13),
        strip.text=element_text(size=15),
        strip.background=element_rect(fill='#F3F3F3'))

ggdraw(p) +
  draw_image("table.png", x = .54, y = .32, width = 0.7, height = 0.55)





# final ====
# Reorder data using average? Learn more about reordering in chart #267
temp <-  


# Plot
dat <-  subset(temp_causes, geo == 'EL' & age == "TOTAL" & sex != "T"
              & cause == "Suicide")

dat <- reshape(dat, idvar = c("year"), timevar = "sex", direction = "wide")
dat <- dat[,c("year", "value.F", "value.M")]
names(dat) <- c("year", "male", "female")
dat$year <- as.factor(dat$year)
head(dat)

ggplot(dat) +
  geom_segment( aes(x=year, xend=year, y=male, yend=female), color="black", size=2, alpha=0.3) +
  geom_point( aes(x=year, y=male, color="male"), size=4 ) +
  geom_point( aes(x=year, y=female, color="female"), size=4 ) +
  labs(title='Suicide Rates in Greece, Females vs Males',
       y='Suicide Rate',
       x='Year') +
  scale_colour_manual(name = 'Gender', 
                      values =c('male' =rgb(0.2,0.7,0.1,0.5), "female" = rgb(0.7,0.2,0.1,0.5)), 
                      labels = c("Males", "Females")) +
  theme(legend.title=element_text(size=16),
        legend.text=element_text(size=13),
        plot.title=element_text(size=21, hjust = 0.5),
        axis.title=element_text(size=16),
        axis.text=element_text(size=13),
        strip.text=element_text(size=15),
        strip.background=element_rect(fill='#F3F3F3'),
        axis.text.y = element_text(angle = 45, vjust=-.5))

