
function calculateAQI(pm_value, pm_type) {
    let breakpoints, aqi_ranges;

    if (pm_type === 'PM2.5') {
        breakpoints = [0, 12, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else if (pm_type === 'PM10') {
        breakpoints = [0, 55, 155, 255, 355, 425, 505, 605];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else {
        return null;
    }

    pm_value = parseFloat(pm_value);

    if (isNaN(pm_value)) {
        return null;
    }

    let index = 0;
    while (index < breakpoints.length && pm_value > breakpoints[index]) {
        index++;
    }

    if (index === 0) {
        return Math.round((aqi_ranges[index] / breakpoints[index]) * pm_value);
    } else if (index === breakpoints.length) {
        return Math.round((aqi_ranges[index - 1] / breakpoints[index - 1]) * pm_value);
    } else {
        const aqi = ((aqi_ranges[index] - aqi_ranges[index - 1]) / (breakpoints[index] - breakpoints[index - 1])) * (pm_value - breakpoints[index - 1]) + aqi_ranges[index - 1];
        return Math.round(aqi);
    }
}



const testCases = [
    { pm_value: 10, pm_type: 'PM2.5', expected: 42 },
    { pm_value: 70, pm_type: 'PM10', expected: 160 },
    { pm_value: 200, pm_type: 'PM2.5', expected: 300 },
    { pm_value: 500, pm_type: 'PM10', expected: 500 },
];

//test cases
testCases.forEach((testCase, index) => {
    const { pm_value, pm_type, expected } = testCase;
    const result = calculateAQI(pm_value, pm_type);
    console.log(`Test Case ${index + 1}:`);
    console.log(`Input: PM Value = ${pm_value}, PM Type = ${pm_type}`);
    console.log(`Expected Output: ${expected}`);
    console.log(`Actual Output: ${result}`);
    console.log(`Test Result: ${result === expected ? 'Passed' : 'Failed'}`);
    console.log('------------------------');
});
