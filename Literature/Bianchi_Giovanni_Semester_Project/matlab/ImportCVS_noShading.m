%% Import data from text file.
% Script for importing data from the following text file:


clear

%% Initialize variables.
filename = 'room_v14_4_hourly_si.csv';
delimiter = ',';

%% Format string for each line of text:
%   column1: text (%s)
%	column2: text (%s)
%   column3: text (%s)
%	column4: text (%s)
%   column5: text (%s)
%	column6: text (%s)
% For more information, see the TEXTSCAN documentation.
formatSpec = '%s%s%s%s%s%s%[^\n\r]';

%% Open the text file.
fileID = fopen(filename,'r');

%% Read columns of data according to format string.
% This call is based on the structure of the file used to generate this
% code. If an error occurs for a different file, try regenerating the code
% from the Import Tool.
dataArray = textscan(fileID, formatSpec, 'Delimiter', delimiter, 'EmptyValue' ,NaN, 'ReturnOnError', false);

%% Close the text file.
fclose(fileID);

%% Post processing for unimportable data.
% No unimportable data rules were applied during the import, so no post
% processing code is included. To generate code which works for
% unimportable data, select unimportable cells in a file and regenerate the
% script.

%% Allocate imported array to column variable names
DateTime = dataArray{:, 1};
DIVAPERIMETERZONE = dataArray{:, 2};
LightingKkWh = dataArray{:, 3};
InteriorEquipmentkWh = dataArray{:, 4};
HeatingEnergykWh = dataArray{:, 5};
CoolingEnergyTONHrH = dataArray{:, 6};

DateTime = DateTime(2:8762);
DIVAPERIMETERZONE = cellfun(@str2num,DIVAPERIMETERZONE(2:8761));
LightingKkWh = cellfun(@str2num,LightingKkWh(2:8761));
InteriorEquipmentkWh = cellfun(@str2num,InteriorEquipmentkWh(2:8761));
HeatingEnergykWh =cellfun(@str2num,HeatingEnergykWh(2:8761));
CoolingEnergykWh = cellfun(@str2num,CoolingEnergyTONHrH(2:8761)).*3.5168;


%% Clear temporary variables
clearvars filename delimiter formatSpec fileID dataArray ans CoolingEnergyTONHrH;