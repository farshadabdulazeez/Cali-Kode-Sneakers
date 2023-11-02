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
        console.log(grand_total);
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
                            // alert(response_a.razorpay_payment_id);
                            var data = {
                                "address_id" : address_id,
                                "grand_total": grand_total,
                                "payment_method": "Razorpay",
                                "payment_id": response_a.razorpay_payment_id,
                                csrfmiddlewaretoken: token
                            };
                            $.ajax({
                                method: "POST", 
                                url: "/order/online-payment/",
                                data: data,
                                success: function(response_b) {
                                    console.log(response_b.order_id);
                                    var order_id=response_b.order_id
                                    swal('Your Payment is Confirmed!', response_b.status, "success").then(function(value) {
                                        window.location.href = '/order/order-confirmed/?order_id=' + order_id + '/';
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