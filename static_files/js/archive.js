document.querySelector(`.nav-link`).style.cssText=`color: #ffffff !important;text-shadow: 0;font-weight: normal;`;
document.querySelector(`.archive-link`).style.cssText=`color: #2cb8f5 !important;text-shadow: 1px 1px 16px #2cb8f5;font-weight: bolder;`;
Chart.defaults.color="#ffffff"
Chart.defaults.font.size=16
get_chart_data = async (chart_id)=>{
    await fetch(base_url + `get-archive-count/?chart_id=${chart_id}`)
    .then(response => response.json())
    .then(result => {
        var chart_ids=result.data.charts_id;
        chart_ids.forEach(element => {
            var canvas_element=document.createElement('canvas');
            canvas_element.setAttribute('id',`chart${element}`);
            document.querySelector('#charts_div').appendChild(canvas_element);

            fetch(base_url + `get-chart-data-archive/?chart_pk=${element}`)
            .then(response => response.json())
            .then(result => {
                var config = create_chart(result,"archive");
                var ctx = canvas_element.getContext('2d');
                const myChart = new Chart(ctx, config)
            })
        });
    })
}

document.querySelector(`.chart_1`).style.cssText=`color: #2cb8f5 !important;text-shadow: 1px 1px 16px #2cb8f5;font-weight: bolder;`;
get_chart_data(1)


for (let index = 1; index < 21; index++) {
    $(document).ready(function () {
        $(`.chart_${index}`).click(function () {
            document.querySelectorAll('.side-links').forEach(element=>element.style.cssText=`color: #ffffff !important;text-shadow: 0;font-weight: bolder;`);
            document.querySelector(`.chart_${index}`).style.cssText=`color: #2cb8f5 !important;text-shadow: 1px 1px 16px #2cb8f5;font-weight: bolder;`;
            document.querySelector('#charts_div').innerHTML="";
            get_chart_data(index)
        });
    });   
}