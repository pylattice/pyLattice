%Joh: Reverse engineered functionality for roundConstr in llsm-tools
% This function is used for reverting double x,y,z coordinates into indexes
% To prevent these indexes from going too low or too high

function B = roundConstr(A,constraint)
    B = round(A,0);
    % replace all values below 1 with 1
    B(B < 1) = 1;
    % replace all values above constraint with constraint
    B(B > constraint-1) = constraint-1;
    
end