% Load CSV data
data = readtable('data.csv');
dates = data(:, 1).RefugeesDate;
refugees = data(:, 2).NoRefugees;

% Task 1: Generate random data
mean_refugees = mean(refugees);
std_refugees = std(refugees);
random_data = mean_refugees + std_refugees * randn(size(refugees));

% Plot original data and random data
figure;
plot(dates, refugees, 'b', dates, random_data, 'r');
title('Original Data vs Random Data (Normal Distribution)');
xlabel('Date');
ylabel('Number of Refugees');
legend('Original Data', 'Random Data (Normal Distribution)');

% Task 2: Compute correlation
correlation = corr(refugees, random_data);
disp(['Correlation: ', num2str(correlation)]);


% Task 3: similiarities
% Euclidean distance
euclidean_distance = norm(refugees - random_data);

% Minkowski distance (with p = 1)
p = 1;
minkowski_distance = nthroot(sum(abs(refugees - random_data).^p), p);

disp(['Euclidean Distance: ', num2str(euclidean_distance)]);
disp(['Minkowski Distance (p=3): ', num2str(minkowski_distance)]);

% Task 4: Peaks and patterns:
running_average = movmean(refugees, 22); % Compute running average
peak_indices = find(refugees(1:end-2) > 1.5 * running_average(1:end-2) & refugees(2:end-1) > running_average(2:end-1) & refugees(3:end) > running_average(3:end));
disp(['Peak indices: ', num2str(peak_indices)]);

diff_sequence = sign(diff(refugees)); % Compute difference sequence
pattern_indices = [];
for i = 1:length(diff_sequence)-3
    % Check if the sequence matches the patterns
    
    if (all(transpose(diff_sequence(i:i+3)) == [1 1 -1 -1])  || all(transpose(diff_sequence(i:i+3)) == [1 -1 1 -1]))
        pattern_indices = [pattern_indices, i];
    end
end
disp(['Pattern indices: ', num2str(pattern_indices)]);

% Plot original data
figure;
plot(dates, refugees, 'b');
hold on;

% Plot peaks
scatter(dates(peak_indices+1), refugees(peak_indices+1), 'r', 'filled'); % Adjust indices to match the original data

% Plot pattern indices
scatter(dates(pattern_indices+1), refugees(pattern_indices+1), 'g', 'filled'); % Adjust indices to match the original data

hold off;
title('Original Data with Peaks and Patterns');
xlabel('Date');
ylabel('Number of Refugees');
legend('Original Data', 'Peaks', 'Patterns');