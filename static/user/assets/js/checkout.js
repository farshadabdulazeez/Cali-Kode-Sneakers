$(document).ready(function () {
    
    $('.razorpayPayment').click(function (e) { 
        e.preventDefault();

        var payment_method = $("[name=payment_method]").val();
        console.log(payment_method);

        $.ajax({
            method: "GET",
            url: "/proceed-to-pay",
            success: function (response) {
                console.log(response);
            }
        });

        // var options = {
        //     "key" : "YOUR_KEY_ID",
        //     "amount" : "50000",
        //     "currency" : "INR",
        //     "name" : "Acme ",
        //     "description" : "Test Transaction",
        //     "image" : "https://example.com/your_logo",
        //     "order_id" : "order_9A33XW170gUtm",
        //     "handler" : function (response){
        //         alert(response.razorpay_payment_id);
        //         alert(response.razorpay_order_id);
        //         alert(response.razorpay_signature);
        //     },
        //     "prefill": {
        //         "name": "Gaurav Kumar",
        //         "email": "gaurav.kumar@example.com",
        //         "contact": "9000090000"
        //     },
        //     "notes": {
        //         "address": "Razorpay Corporate Office"
        //     },
        //     "theme": {
        //         "color": "#3399cc"
        //     }
        // };
        // var rzp1 = new Razorpay(options);
        // rzp1.open();
        
    });

});