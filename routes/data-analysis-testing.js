router.get('/data-analysis-testing', (req,res) => {
    const monitorId = req.body.monitorId;

    //For now, let's just render a page that displays a monitor ID prompt
    res.render("data-analysis", { monitorId: monitorId });
})

function handleFormSubmission(event) {
    event.preventDefault(); 
    
    const monitorIdInput = document.getElementById('monitorId');
    const enteredMonitorId = monitorIdInput.value;

    const validMonitorIds = [
        "MOD-PM-00645", "MOD-PM-00642", "MOD-PM-00636", "MOD-PM-00637", "MOD-PM-00651",
        "MOD-PM-00665", "MOD-PM-00678", "MOD-PM-00687", "MOD-PM-00703", "MOD-PM-00691",
        "MOD-PM-00695", "MOD-PM-00671", "MOD-PM-00676", "MOD-PM-00692", "MOD-PM-00661",
        "MOD-PM-00166", "MOD-PM-00677", "MOD-PM-00704", "MOD-PM-00681", "MOD-PM-00688",
        "MOD-PM-00682", "MOD-PM-00673", "MOD-PM-00672", "MOD-PM-00666", "MOD-PM-00656",
        "MOD-PM-00654", "MOD-PM-00639", "MOD-PM-00662", "MOD-PM-00668", "MOD-PM-00655",
        "MOD-PM-00709", "MOD-PM-00684", "MOD-PM-00674", "MOD-PM-00659", "MOD-PM-00653",
        "MOD-PM-00641", "MOD-PM-00638", "MOD-PM-00635", "MOD-PM-00683", "MOD-PM-00711",
        "MOD-PM-00640", "MOD-PM-00675", "MOD-PM-00646", "MOD-PM-00696", "MOD-PM-00652",
        "MOD-PM-00660"
    ];

    // Check if entered monitor ID is valid
    const isValidMonitorId = validMonitorIds.some(id => enteredMonitorId.toUpperCase() === id.toUpperCase());

    if (isValidMonitorId) {
        alert("Correct Monitor ID.");
    } else {
        alert("Incorrect monitor ID. Please enter a valid Monitor ID.");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.needs-validation');
    form.addEventListener('submit', handleFormSubmission);
});