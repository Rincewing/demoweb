#!/usr/bin/perl -w

# Edited from the code for a solution to COMP2041/9041 assignment 2, S2 2015
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/
# Starting code created by Andrew Taylor, improved then repourposed by Jens Waring

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;
use Scalar::Util qw(looks_like_number);
use Date::Format;

sub main() {
    # print start of HTML ASAP to assist debugging if there is an error in the script (only when there are no cookies)
    print "Content-type: text/html\n\n";
    print "<!DOCTYPE html>\n";

    # Now tell CGI::Carp to embed any warning in HTML and set debugging output
    warningsToBrowser(1);
    $debug = 1;

    # Get cookies
    %cookies = CGI::Cookie->fetch;
    if (! defined $cookies{'UNAME'}) {
        $authUser = "";
    } else {
        $authUser = $cookies{'UNAME'}->value;
        if ($debug) {
            print "Cookies found - value $authUser.\n";
        }
    }

    # define some global variables, process inputs and clean parameters
    $users_dir = "dataset/accounts";

    $page = "user_page";
    my $score = param('Leaderboard') || "";
    my $play = param('Play') || "";
    my $buy = param('Buy Skins') || "";
    my $profile = param('Profile') || "";
    my $login = param('Login') || "";
    my $logout = param('Logout') || "";
    my $register = param('Register') || "";
    if ($logout) {
        $authUser = "";
    }
    my $html = "";

    # Now the content
    if ($authUser) {
        $html .= auth_menu();
        if ($play) {
            $html .= play();
        } elsif ($buy) {
            $html .= buy_skins();
        } elsif ($score) {
            $html .= leaderboard();
        } else {
            $html .= user_page();
        }
    } else {
        $html .= unauth_menu();
        if ($login) {
            $html .= login();
        elsif ($register) {
            $html .= register();
        else {
            $html .= leaderboard();
        }
    }

    # Now print everything out (delayed because of cookies and some debugging output)
    $cookieUname = CGI::Cookie->new(-name=>'UNAME',-value=>"$authUser");
    print "<meta http-equiv=\"set-cookie\" content=\"$cookieUname\">\n";
    print page_header();
    print $html;
    print page_trailer();
}




sub login() {
    my $username = param('Username') || '';
    my $password = param('Password') || '';
    my $actualPassword = '';
    if ($username && $password) {
        if (! open (F, "$users_dir/$username/details.txt")) {
            $returnHTML .= "Unknown username!\n";
            $returnHTML .= start_form . "\n";
            $returnHTML .= submit(value => "Try Again") . "\n";
            $returnHTML .= end_form . "\n";
        } else {
            while (my $line = <F>) {
                if ($line =~ /password: (.*)/gi) {
                    $actualPassword = $1;
                }
            }
            chomp $actualPassword;

            if ($debug) {
                $returnHTML .= "<!-- actualPassword=$actualPassword -->\n";
            }

            if ($password eq $actualPassword) {
                $authUser = $username;
                $returnHTML .= "$username authenticated.\n";
                $returnHTML .= start_form . "\n";
                $returnHTML .= submit(value => Continue) . "\n";
                $returnHTML .= end_form . "\n";
            } elsif ($username && $password) {
                $returnHTML .= "Incorrect password!\n";
                $returnHTML .= start_form . "\n";
                $returnHTML .= submit(value => "Try Again") . "\n";
                $returnHTML .= end_form . "\n";
            }
        }
    } else {
        $returnHTML .= start_form . "\n";
        if ($username) {
            $returnHTML .= hidden('username') . "\n";
        } else {
            $returnHTML .= "Username:\n" . "<input type=\"text\" name=\"username\" value=\"\" />" . "\n";
        }
        if ($password) {
            $returnHTML .= hidden('password') . "\n";
        } else {
            $returnHTML .= "Password:\n" . "<input type=\"password\" name=\"password\" value=\"\" />" . "\n";
        }
        $returnHTML .= submit(value => Login) . "\n";
        $returnHTML .= end_form . "\n";
    }
    return $returnHTML;
}

sub register() {
# TODO
}

#
# Page header
#
sub auth_menu {
    my $retVal = "<div class=\"bitter_menu\">\n";
    $retVal .= "<ul>\n";
    $retVal .= "<bitter_list><bitter_menu_element>Welcome, $authUser.</bitter_menu_element></bitter_list>\n<br><br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . logout() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . profile() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . play() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . buy_skins() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . leaderboard() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . profile() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "</ul>\n";
    $retVal .= "</div>\n<br>\n";
    return $retVal;
}
sub unauth_menu {
    my $retVal = "<div class=\"bitter_menu\">\n";
    $retVal .= "<ul>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . login() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . register() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "<bitter_list><bitter_menu_element>" . leaderboard() . "</bitter_menu_element></bitter_list>\n<br>\n";
    $retVal .= "</ul>\n";
    $retVal .= "</div>\n<br>\n";
    return $retVal;
}

#
# Buttons in the menu
#
sub register() {
    my $retVal = start_form . "\n";   # Format details (add a class later)
    $retVal .= submit(register => "Register") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub login() {
    my $retVal = start_form . "\n";   # Format details
    $retVal .= submit(login => "Login") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub logout() {
    my $retVal = start_form . "\n";   # Format details (add a class later)
    $retVal .= submit(logout => "Logout") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub play() {
    my $retVal = start_form . "\n";   # Format details
    $retVal .= submit(play => "Play") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub leaderboard() {
    my $retVal = start_form . "\n";   # Format details
    $retVal .= submit(leaderboard => "Leaderboard") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub buy_skins() {
    my $retVal = start_form . "\n";   # Format details
    $retVal .= submit(buy_skins => "Buy Skins") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

sub profile() {
    my $retVal = start_form . "\n";   # Format details
    $retVal .= submit(profile => "Profile") . "\n";
    $retVal .= end_form . "\n";  # Format details
    return $retVal;
}

#
# Show details of the logged in user
#
sub user_page() {
    my $userToShow = $authUser;
    my $retVal = "";

    my $details_filename = "$users_dir/$userToShow/details.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    my %details = ();

    for $line (<$p>) {
        my $detail = "";
        if ($line =~ /password:\ /gi) {
            next;
        } elsif ($line =~ /^(.*):/) {
            $line =~ s/_/\ /;
            $details{$1} = "$line\n";
        } else {
            $details{my $i++} = "$line\n";
        }
    }

    close $p;
    my $next_user = $userNum + 1;
    my %seen = ();
    $retVal = "<div class=\"bitter_user_details\">\n";
    $retVal .= "<img src=\"$image_filename\" alt=\"No profile image\" style=bitter_profile>\n";
    for $key ("username", "hiscore", keys %details) {
        if (defined $details{$key} && !defined $seen{$key}) {
            $retVal .= $details{$key};
            $seen{$key} = 1;
        }
    }
    $retVal .= "</div>\n";
    return $retVal;
}

sub play() {
# TODO
}

sub buy_skins() {
# TODO
}

sub leaderboard() {
# TODO
}

sub user_page() {
# TODO
}


#
# HTML placed at the top of every page
#
sub page_header {
    return <<eof

<html lang="en">
<head>
<title>Bitter</title>
<link href="bootstrap.min.css" rel="stylesheet">
<link href="bitter.css" rel="stylesheet">
</head>
<body>
<div class="bitter_heading">
Bitter
</div>
<div class="container">
eof
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "</div>\n";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

main();
