jQuery(document).ready(function($) {
    console.log("Document is ready");

    $('.razorpayPayment').click(function(e) {
        e.preventDefault();

        var name = $("[name='name']").val();
        var mobile = $("[name='mobile']").val();
        var address_id = $("[name='address_id']").val();
        var address = $("[name='address']").val();
        var landmark = $("[name='landmark']").val();
        var city = $("[name='city']").val();
        var pincode = $("[name='pincode']").val();
        var district = $("[name='district']").val();
        var state = $("[name='state']").val();
        var grand_total = $("[name='grand_total']").val();
        var token = $("[name='csrfmiddlewaretoken']").val();

        console.log(address_id, grand_total);

        if (name == "" || mobile == "" || address_id == "" || address == "" || landmark == "" || city == "" || pincode == "" || district == "" || state == "" || grand_total == "") {
            return false;
        } else {
            console.log("else case running here");
            data = {
                "grand_total": grand_total,
            }
            $.ajax({
                method: "GET",
                url: "/order/proceed-to-pay/",
                data:data,
                success: function(response) {
                    console.log(response.total_amount);

                    var options = {
                        "key": "rzp_test_Ijcik5oUgxAy5l",
                        "amount": response.total_amount * 100,
                        "currency": "INR",
                        "name": "Cali Kode Sneakers",
                        "description": "Thank you for shopping with us",
                        "image": "https://example.com/your_logo",
                        "handler": function(response_a) {
                            alert(response_a.razorpay_payment_id);
                            var data = {
                                "address_id" : address_id,
                                "grand_total": grand_total,
                                "payment_method": "Razorpay",
                                "payment_id": response_a.razorpay_payment_id,
                                csrfmiddlewaretoken: token
                            };
                            $.ajax({
                                method: "POST", 
                                url: "online-payment/",
                                data: data,
                                success: function(response_b) {
                                    console.log(response_b.order_id);
                                    swal('Congratulations!', response_b.status, "success").then(function(value) {
                                        window.location.href = 'order-confirmed/' + order_id + '/';
                                    });
                                }
                            });
                        },
                        
                        "prefill": {
                            "name": name,
                            "contact": mobile
                        },

                        "theme": {
                            "color": "#3399cc"
                        }
                    };

                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                },
                error: function(xhr, status, error) {
                    console.log('ajax error');
                    console.error("AJAX request error: " + error);
                }
            });
        }
    });
});


// $(document).ready(function () {
//     console.log("Document is ready");
//     $('.razorpayPayment').click(function (e) { 
//         e.preventDefault();
//         console.log("2");
//         var name = $("#name").val();
//         var mobile = $("#mobile").val();
//         var address = $("#address").val();
//         var landmark = $("#landmark").val();
//         var city = $("#city").val();
//         var pincode = $("#pincode").val();
//         var district = $("#district").val();
//         var state = $("#state").val();
//         var grand_total = $("#grand_total").val();
//         var token = $("[name='csrfmiddlewaretoken']").val();

//         if(name == "" || mobile == "" || address == "" || landmark == "" || city == "" || pincode == "" || district == "" || state == "" || grand_total == "") { 
//             console.log("3");
//             return false;
//         } else {
//             console.log("4");
//             $.ajax({
//                 method: "GET",
//                 url: "proceed-to-pay/",
//                 success: function (response) {
//                     // console.log(response)
//                     var options = {
//                         "key" : "rzp_test_Ijcik5oUgxAy5l",
//                         "amount" : response.total_amount * 100,
//                         "currency" : "INR",
//                         "name" : "Cali Kode Sneakers",
//                         "description" : "Thank you for shopping with us",
//                         "image" : "https://example.com/your_logo",
//                         "handler" : function (response_a) {
//                             alert(response_a.razorpay_payment_id);
//                             var data = {
//                                 "name" : name,
//                                 "mobile" : mobile,
//                                 "address" : address,
//                                 "landmark" : landmark,
//                                 "city" : city,
//                                 "pincode" : pincode,
//                                 "district" : district,
//                                 "state" : state,
//                                 "grand_total" : grand_total,
//                                 "payment_method" : "Razorpay",
//                                 "payment_id" :  response_a.razorpay_payment_id,
//                                 csrfmiddlewaretoken: token
//                             };

//                             $.ajax({
//                                 type: "POST",
//                                 url: "online-payment/",
//                                 data: data,
//                                 success: function (response_b) {
//                                     swal('Congratulations!', response_b.status, "success").then((value) => {
//                                         window.location.href = 'online-payment/' + order_id + '/';
//                                     });
//                                 }
//                             });
//                         },
//                         "prefill": {
//                             "name": name,
//                             "contact": mobile
//                         },
//                         "notes": {
//                             "address": "Razorpay Corporate Office"
//                         },
//                         "theme": {
//                             "color": "#3399cc"
//                         }
//                     };
//                     var rzp1 = new Razorpay(options);
//                     rzp1.open();
//                 }
//             });
//         }
//     });

// });
