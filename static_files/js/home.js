document.querySelector(`.nav-link`).style.cssText=`color: #ffffff !important;text-shadow: 0;font-weight: normal;`;
document.querySelector(`.home-link`).style.cssText=`color: #2cb8f5 !important;text-shadow: 1px 1px 16px #2cb8f5;font-weight: bolder;`;
Chart.defaults.color="#ffffff"
Chart.defaults.font.size=14
Chart.defaults.width=850
Chart.defaults.height=450

const userAction = async (index) => {
    const response = await fetch(base_url + `chart-data-home/?chart_id=${index+1}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json())
        .then(result => {
            var config = create_chart(result,null);
            const ctx = document.querySelector(`#chart${index+1}`).getContext('2d');
            const myChart = new Chart(ctx, config)
        })
}
async function getChart() {
    for (let index = 0; index < 20; index++) {
        await userAction(index);
    }
}

getChart()


for (let index = 1; index < 21; index++) {
    $(document).ready(function () {
        $(`.chart_${index}`).click(function () {
            $("html, body").animate({
                scrollTop: $(`#chart${index}`).offset().top - 100,
            }, "slow");
            return false;
        });
    });   
}

$(window).scroll(function () {
    if ($(this).scrollTop() > 50) {
        $('.navbar').addClass('newClass');
    } else {
        $('.navbar').removeClass('newClass');
    }
});