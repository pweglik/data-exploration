% Load CSV data
data = readtable('data.csv');
dates = data(:, 1).RefugeesDate;
refugees = data(:, 2).NoRefugees;

% Task 1: Calculate absolute and relative change, logarithmic change, mean, and standard deviation
abs_change = diff(refugees);
rel_change = diff(refugees) ./ refugees(1:end-1);
log_change = diff(log(refugees));
mean_refugees = mean(refugees);
std_refugees = std(refugees);

% Plot
figure;
subplot(2, 2, 1);
plot(dates(2:end), abs_change);
title('Absolute Change');
xlabel('Date');
ylabel('Change');

subplot(2, 2, 2);
plot(dates(2:end), rel_change);
title('Relative Change');
xlabel('Date');
ylabel('Change');

subplot(2, 2, 3);
plot(dates(2:end), log_change);
title('Logarithmic Change');
xlabel('Date');
ylabel('Change');


% Task 2
d = posixtime(dates);

p_linear = polyfit(d, refugees, 1);
linear_approx = polyval(p_linear, d);
error_linear = refugees - linear_approx;

figure;
plot(dates, refugees, 'b', dates, linear_approx, 'r--');
hold on;

for i = 1:length(dates)
    line([dates(i) dates(i)], [linear_approx(i) refugees(i)], 'Color', 'g');
end

hold off;
title('Linear Approximation with Residuals');
xlabel('Date');
ylabel('Number of Refugees');
legend('Original Data', 'Linear Trend', 'Residuals');

% Task 3: Smooth data with moving average, k = 10 and k = 20
smoothed_10 = movmean(refugees, 10);
smoothed_20 = movmean(refugees, 20);

figure;
plot(dates, refugees, 'b', dates, smoothed_10, 'r', dates, smoothed_20, 'g');
title('Comparison of Unsmoothed and Smoothed Time Series');
xlabel('Date');
ylabel('Number of Refugees');
legend('Original', 'Smoothed (k=10)', 'Smoothed (k=20)');

% Task 4: Approximate data with polynomial of degree 4
p_poly = polyfit(d, refugees, 4);
poly_approx = polyval(p_poly, d);

% Plot polynomial approximation
figure;
plot(dates, refugees, 'b', dates, poly_approx, 'r');
title('Polynomial Approximation of Data');
xlabel('Date');
ylabel('Number of Refugees');
legend('Original', 'Polynomial Approximation');
% Task 5
% Srednia ruchoma jest standardowym, w problemie timeseries, sposoebem wygładzania danych. Dane przypominają oryginalna postać tylko nagłe skoki zostają rozłożone na więcej (k) punktów czasowych. Metoda dopasowania wielomianu zupełnie się nie sprawdza. Być może ma prawo zadziałać dla prostych szeregów czasowych, ale dla bardziej skoplikowanych nie da sobie rady, co widać już na naszym przykładzie.