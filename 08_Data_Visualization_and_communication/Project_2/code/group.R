# Package names
packages <- c("ggplot2", 
              "ggmap")

# Load dplyr
library(dplyr)

# Load geosphere
library(geosphere)
library(ggplot2)
library(sf)
library(lubridate)


data <- read.csv(file=".\map_data.csv")
data
data$End.LATITUDE<-as.character(data$End.LATITUDE)
data$End.LONGITUDE<-as.character(data$End.LONGITUDE)
data$Start.LATITUDE<-as.character(data$Start.LATITUDE)
data$Start.LONGITUDE<-as.character(data$Start.LONGITUDE)

# Group by count using dplyr
agg_tbl <- data %>% group_by(Start.station, Start.LATITUDE, Start.LONGITUDE, End.station, End.LATITUDE, End.LONGITUDE) %>% 
  summarise(total_count=n())
agg_tbl <- na.omit(agg_tbl)
agg_tbl_50 <- head(agg_tbl[order(agg_tbl$total_count,  decreasing = TRUE),], n=500)
agg_tbl_50


library(lubridate)

data <- read.csv(file=".\map_data.csv")

data$year <- strptime(data$Start.date, "%Y")
agg_tbl <- data %>% 
  group_by(Start.station, year) %>%
  summarise(Unique_Elements = n_distinct())
agg_tbl <-agg_tbl[order(agg_tbl$year,  decreasing = FALSE),]

agg_tbl_final <- agg_tbl %>% 
  group_by(year) %>%
  summarise(n_of_stations = n())
agg_tbl_final <-agg_tbl_final[order(agg_tbl_final$year,  decreasing = FALSE),]
agg_tbl_final$year <- year(agg_tbl_final$year)
agg_tbl_final


# Create dataset
data <- data.frame(
  id=c(2016, 2017, 2018),
  individual=c(2016, 2017, 2018),
  value=c(370, 452, 499)
)

# Make the plot
p <- ggplot(agg_tbl_final, aes(x=as.factor(id), y=n_of_stations/499, fill=id)) + 
  
  # This add the bars with a blue color
  geom_bar(aes(x=as.factor(year), y=n_of_stations/499, fill=year), stat="identity", alpha=0.5) +
  ylim(-0.8,1) +
  # Custom the theme: no axis title and no cartesian grid
  theme_minimal() +
  theme(
    axis.text = element_blank(),
    axis.title = element_blank(),
    panel.grid = element_blank()     # This remove unnecessary margin around plot
  ) +
  
  # This makes the coordinate polar instead of cartesian.
  coord_polar(start = 0)
p


agg_tbl_final
